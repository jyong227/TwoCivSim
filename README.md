How it Works:

Civilization Class:

Stores the name, core characteristics (intelligence, tech_rate, aggressiveness, cooperation), and state variables (population, resources, tech_level, is_alive).
__init__: Initializes a new civilization.
calculate_strength(): Determines combat/influence power, heavily weighted by technology.
gather_resources(): Increases resources based on population and tech.
consume_resources(): Decreases resources based on population. Handles starvation if resources run out.
grow_population(): Increases population based on available resources and cooperation (representing internal stability).
develop_technology(): Increases tech level based on intelligence, tech rate, and resources spent. Higher tech levels become harder to achieve.
die(): Marks the civilization as eliminated.
display_status(): Prints the current state.
run_simulation() Function:

Takes two Civilization objects and the number of turns.
Main Loop: Iterates through each turn.
Internal Phase: Each surviving civilization gathers/consumes resources, grows population, and develops technology independently. Checks for death by starvation.
Interaction Phase:
Calculates combined aggressiveness and cooperation.
Calculates relative strength.
Conflict Check: Determines if conflict occurs based on aggression levels, relative strength, and some randomness. If conflict happens:
Determines attacker/defender.
Calculates losses for both sides based on relative strength, tech levels, and randomness. Population and resources are reduced.
Checks if either civilization was eliminated by the conflict.
Cooperation Check: If no conflict occurs, checks if cooperation happens based on cooperation levels and randomness. If cooperation happens:
Both civilizations gain small resource and tech bonuses, influenced by the partner's traits.
No Interaction: If neither threshold is met, nothing happens between them this turn.
Display Status: Shows the state of both civs after the turn's events.
End Conditions: The loop breaks if a civ is eliminated or the maximum number of turns is reached.
Setup (if __name__ == "__main__":)

Creates two example Civilization instances with different characteristics. You can easily change these values to see different outcomes.
Sets the total number of turns for the simulation.
Calls run_simulation.
Prints a final summary.
Possible Extensions & Improvements:

More Complex Resource System: Food, Production, Materials, etc.
Geography/Map: Place civs on a map, introduce distance, terrain effects, expansion.
Multiple Civilizations: Modify the interaction logic to handle more than two civs.
Diplomacy: More nuanced states than just Fight/Cooperate (e.g., Alliances, Trade Agreements, Non-Aggression Pacts).
Culture/Happiness: Add internal factors affecting stability and productivity.
Military Units: Differentiate military strength from general population/tech.
Events: Random events like natural disasters, plagues, resource booms, great leaders.
User Interface: Use libraries like Pygame or Tkinter for a visual representation.
More Sophisticated Formulas: Use non-linear formulas for growth, tech cost, combat outcomes, etc.
Saving/Loading: Allow saving the state of a simulation.
