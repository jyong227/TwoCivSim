import random
import math

# --- Simulation Constants ---
INITIAL_POPULATION = 1000
INITIAL_RESOURCES = 500
INITIAL_TECH_LEVEL = 1.0

POP_GROWTH_RATE_BASE = 0.01  # Base population growth per turn
RESOURCE_GATHER_BASE = 0.5   # Base resources gathered per person per turn
TECH_IMPROVEMENT_BASE = 0.01 # Base tech points gained per turn

# Interaction Thresholds
CONFLICT_THRESHOLD_AGG = 6.0   # If combined agg > this, potential conflict
COOPERATION_THRESHOLD_COOP = 12.0 # If combined coop > this, potential cooperation
STRENGTH_DIFF_AGG_MOD = 1.5  # If one civ is this much stronger, aggression more likely

# Resource Costs
POP_RESOURCE_COST = 0.1  # Resources consumed per person per turn
TECH_RESOURCE_COST = 50   # Resources needed per tech point research

# Combat Modifiers
STRENGTH_ADVANTAGE_FACTOR = 1.2 # How much stronger attacker needs to be for easy win
COMBAT_LOSS_BASE = 0.1        # Base percentage loss in combat
TECH_COMBAT_FACTOR = 1.5      # How much tech level influences combat strength exponent

# Cooperation Benefits
COOP_RESOURCE_BONUS = 0.05   # % resource bonus from cooperation
COOP_TECH_BONUS = 0.02       # Flat tech points bonus from cooperation

class Civilization:
    """Represents a single civilization in the simulation."""

    def __init__(self, name, intelligence, tech_rate, aggressiveness, cooperation):
        self.name = name

        # Core Characteristics (Scale often 1-10, but can be adjusted)
        self.intelligence = max(1, intelligence) # Min 1 to avoid zero division/multiplication issues
        self.tech_rate = max(0.1, tech_rate)     # Min 0.1
        self.aggressiveness = max(0, aggressiveness)
        self.cooperation = max(0, cooperation)

        # State Variables
        self.population = INITIAL_POPULATION
        self.resources = INITIAL_RESOURCES
        self.tech_level = INITIAL_TECH_LEVEL
        self.is_alive = True

    def calculate_strength(self):
        """Calculates the overall strength, heavily influenced by tech."""
        if not self.is_alive:
            return 0
        # Tech has an exponential impact on strength
        return self.population * (self.tech_level ** TECH_COMBAT_FACTOR)

    def gather_resources(self):
        """Gather resources based on population and tech level."""
        if not self.is_alive:
            return
        gathered = self.population * RESOURCE_GATHER_BASE * (1 + self.tech_level / 10.0) # Tech improves gathering
        self.resources += gathered
        # print(f"{self.name} gathered {gathered:.2f} resources.") # DEBUG

    def consume_resources(self):
        """Consume resources based on population."""
        if not self.is_alive:
            return
        consumed = self.population * POP_RESOURCE_COST
        self.resources -= consumed
        # print(f"{self.name} consumed {consumed:.2f} resources.") # DEBUG
        if self.resources < 0:
            # Starvation/Resource Depletion leads to population decline
            deficit = abs(self.resources)
            pop_loss = min(self.population, deficit / POP_RESOURCE_COST * 1.5) # Lose pop faster than normal consumption
            print(f"*** {self.name} suffers resource shortage! Loses {pop_loss:.0f} population. ***")
            self.population -= pop_loss
            self.resources = 0
            if self.population <= 0:
                self.die(f"starvation due to resource depletion")

    def grow_population(self):
        """Grow population if resources allow."""
        if not self.is_alive or self.resources <= 0:
            return

        # Growth influenced by resources available beyond basic needs
        resource_factor = max(0, 1 + (self.resources / (self.population * POP_RESOURCE_COST * 5 + 1))) # Simple bonus factor
        growth = self.population * POP_GROWTH_RATE_BASE * resource_factor * (1 + self.cooperation / 20.0) # Cooperation slightly helps internal growth/stability
        self.population += growth
        # print(f"{self.name} population grew by {growth:.0f}.") # DEBUG

    def develop_technology(self):
        """Improve technology based on intelligence and tech rate, consuming resources."""
        if not self.is_alive or self.resources < TECH_RESOURCE_COST: # Need minimum resources to research
            return

        # Tech gain influenced by intelligence, base rate, and current tech (diminishing returns)
        tech_points_potential = self.intelligence * self.tech_rate * TECH_IMPROVEMENT_BASE * (self.population / 1000.0) # More pop = more potential researchers
        tech_points_potential /= (1 + self.tech_level * 0.1) # Harder to advance at higher tech levels

        # Spend resources on research
        resources_to_spend = min(self.resources, tech_points_potential * TECH_RESOURCE_COST)
        tech_points_gained = resources_to_spend / TECH_RESOURCE_COST

        self.resources -= resources_to_spend
        self.tech_level += tech_points_gained
        # print(f"{self.name} spent {resources_to_spend:.2f} resources to gain {tech_points_gained:.4f} tech points.") # DEBUG

    def die(self, reason="elimination"):
        """Marks the civilization as no longer active."""
        print(f"*** {self.name} has been eliminated due to {reason}! ***")
        self.is_alive = False
        self.population = 0
        self.resources = 0
        self.tech_level = 0

    def display_status(self):
        """Prints the current status of the civilization."""
        if not self.is_alive:
            print(f"{self.name}: ELIMINATED")
        else:
            print(f"{self.name}: Pop={self.population:.0f}, Res={self.resources:.0f}, Tech={self.tech_level:.3f}, Str={self.calculate_strength():.0f}")

# --- Simulation Logic ---

def run_simulation(civ1, civ2, num_turns):
    """Runs the main simulation loop."""
    print("--- Starting Simulation ---")
    civ1.display_status()
    civ2.display_status()
    print("-" * 20)

    for turn in range(1, num_turns + 1):
        print(f"\n--- Turn {turn} ---")

        # --- Internal Phase (Growth, Research) ---
        for civ in [civ1, civ2]:
            if civ.is_alive:
                civ.gather_resources()
                civ.consume_resources() # Consume before growth
                if civ.is_alive: # Check again after consumption/starvation
                    civ.grow_population()
                    civ.develop_technology()

        # Check if a civ died during internal phase
        if not civ1.is_alive or not civ2.is_alive:
            civ1.display_status()
            civ2.display_status()
            print("--- Simulation Ended: One civilization eliminated ---")
            break # End simulation if one is dead

        # --- Interaction Phase ---
        interaction_occurred = False
        strength1 = civ1.calculate_strength()
        strength2 = civ2.calculate_strength()
        combined_agg = civ1.aggressiveness + civ2.aggressiveness
        combined_coop = civ1.cooperation + civ2.cooperation

        # Determine relative strength
        stronger_civ = None
        weaker_civ = None
        strength_ratio = 1.0
        if strength1 > strength2 and strength2 > 0:
            strength_ratio = strength1 / strength2
            stronger_civ = civ1
            weaker_civ = civ2
        elif strength2 > strength1 and strength1 > 0:
            strength_ratio = strength2 / strength1
            stronger_civ = civ2
            weaker_civ = civ1

        # 1. Conflict Check
        # More likely if combined aggression is high, or if one is much stronger and aggressive
        will_fight = False
        if combined_agg > CONFLICT_THRESHOLD_AGG * (random.uniform(0.8, 1.2)): # Add some randomness
            will_fight = True
        elif stronger_civ and stronger_civ.aggressiveness > (weaker_civ.aggressiveness + 3) and strength_ratio > STRENGTH_DIFF_AGG_MOD:
             # Much stronger civ is significantly more aggressive -> Opportunistic attack
             if random.random() < (stronger_civ.aggressiveness / 10.0): # Chance based on aggressor's aggression
                 will_fight = True

        if will_fight:
            interaction_occurred = True
            print(f"Interaction: Conflict between {civ1.name} and {civ2.name}!")

            # Determine Attacker (more aggressive one, or random if equal)
            attacker = None
            defender = None
            if civ1.aggressiveness > civ2.aggressiveness:
                attacker, defender = civ1, civ2
            elif civ2.aggressiveness > civ1.aggressiveness:
                attacker, defender = civ2, civ1
            else:
                 attacker, defender = random.sample([civ1, civ2], 2)

            print(f"{attacker.name} (Str {attacker.calculate_strength():.0f}) attacks {defender.name} (Str {defender.calculate_strength():.0f})")

            # Combat Resolution (Simplified)
            s_attacker = attacker.calculate_strength()
            s_defender = defender.calculate_strength()

            # Calculate loss multipliers (based on strength difference and randomness)
            # Advantage reduces defender's effective strength for loss calculation
            defender_effective_strength = s_defender / (1 + max(0, (s_attacker / (s_defender + 1) - 1))) # +1 avoids div by zero
            attacker_loss_mult = COMBAT_LOSS_BASE * (1 + defender_effective_strength / (s_attacker + 1)) * random.uniform(0.7, 1.3)
            defender_loss_mult = COMBAT_LOSS_BASE * (1 + s_attacker / (defender_effective_strength + 1)) * random.uniform(0.7, 1.3)

            # Apply losses (higher tech means less proportional pop loss, more resource loss)
            attacker_pop_loss = attacker.population * attacker_loss_mult * (1 / (1 + attacker.tech_level * 0.1))
            attacker_res_loss = attacker.resources * attacker_loss_mult * (1 + attacker.tech_level * 0.1)

            defender_pop_loss = defender.population * defender_loss_mult * (1 / (1 + defender.tech_level * 0.1))
            defender_res_loss = defender.resources * defender_loss_mult * (1 + defender.tech_level * 0.1)

            # Cap losses
            attacker_pop_loss = min(attacker.population * 0.9, attacker_pop_loss) # Max 90% loss in one go
            attacker_res_loss = min(attacker.resources * 0.9, attacker_res_loss)
            defender_pop_loss = min(defender.population * 0.9, defender_pop_loss)
            defender_res_loss = min(defender.resources * 0.9, defender_res_loss)

            attacker.population -= attacker_pop_loss
            attacker.resources -= attacker_res_loss
            defender.population -= defender_pop_loss
            defender.resources -= defender_res_loss

            print(f"Outcome: {attacker.name} loses {attacker_pop_loss:.0f} pop, {attacker_res_loss:.0f} res. "
                  f"{defender.name} loses {defender_pop_loss:.0f} pop, {defender_res_loss:.0f} res.")

            # Check for elimination post-combat
            if attacker.population <= 1 or attacker.resources < 0: attacker.die("combat losses")
            if defender.population <= 1 or defender.resources < 0: defender.die("combat losses")


        # 2. Cooperation Check (only if no conflict occurred)
        elif combined_coop > COOPERATION_THRESHOLD_COOP * (random.uniform(0.8, 1.2)):
            interaction_occurred = True
            print(f"Interaction: Cooperation between {civ1.name} and {civ2.name}!")

            # Simple benefits: resource gain and slight tech boost
            res_bonus1 = civ1.resources * COOP_RESOURCE_BONUS * (civ2.cooperation / 10.0) # More cooperative partner gives better bonus
            res_bonus2 = civ2.resources * COOP_RESOURCE_BONUS * (civ1.cooperation / 10.0)
            tech_bonus1 = COOP_TECH_BONUS * (civ2.intelligence / 5.0) # More intelligent partner shares more effectively
            tech_bonus2 = COOP_TECH_BONUS * (civ1.intelligence / 5.0)

            civ1.resources += res_bonus1
            civ2.resources += res_bonus2
            civ1.tech_level += tech_bonus1
            civ2.tech_level += tech_bonus2

            print(f"Outcome: {civ1.name} gains {res_bonus1:.0f} res, {tech_bonus1:.4f} tech. "
                  f"{civ2.name} gains {res_bonus2:.0f} res, {tech_bonus2:.4f} tech.")

        # 3. No Interaction
        if not interaction_occurred:
            print("Interaction: None this turn.")

        # --- Display Status ---
        civ1.display_status()
        civ2.display_status()

        # --- Check End Conditions ---
        if not civ1.is_alive or not civ2.is_alive:
            print("--- Simulation Ended: One civilization eliminated ---")
            break
        if turn == num_turns:
            print(f"--- Simulation Ended: Reached turn limit ({num_turns}) ---")
            break

# --- Setup and Run ---
if __name__ == "__main__":
    # Example Civilizations (Adjust these values!)
    # Civ 1: Intelligent, Peaceful Technologists
    civilization1 = Civilization(
        name="Aethel",
        intelligence=8,
        tech_rate=7,
        aggressiveness=2,
        cooperation=8
    )

    # Civ 2: Aggressive, Robust Warriors
    civilization2 = Civilization(
        name="Borog",
        intelligence=4,
        tech_rate=3,
        aggressiveness=9,
        cooperation=2
    )

    # You could also prompt the user for these values:
    # try:
    #     c1_name = input("Enter name for Civilization 1: ")
    #     c1_int = int(input(f"Enter intelligence for {c1_name} (1-10): "))
    #     # ... and so on for other characteristics and Civ 2
    #     # civilization1 = Civilization(c1_name, c1_int, ...)
    #     # civilization2 = Civilization(...)
    # except ValueError:
    #     print("Invalid input. Using default civilizations.")
    #     # Keep the default civs defined above if input fails


    simulation_turns = 100
    run_simulation(civilization1, civilization2, simulation_turns)

    # --- Final Summary ---
    print("\n--- Final State ---")
    civilization1.display_status()
    civilization2.display_status()

    if civilization1.is_alive and civilization2.is_alive:
        s1 = civilization1.calculate_strength()
        s2 = civilization2.calculate_strength()
        if s1 > s2:
            print(f"{civilization1.name} is the dominant civilization.")
        elif s2 > s1:
            print(f"{civilization2.name} is the dominant civilization.")
        else:
            print("The civilizations are roughly equal in strength.")
    elif civilization1.is_alive:
        print(f"{civilization1.name} is the sole survivor.")
    elif civilization2.is_alive:
         print(f"{civilization2.name} is the sole survivor.")
    else:
        print("Both civilizations have been eliminated.")
