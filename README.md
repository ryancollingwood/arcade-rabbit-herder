# arcade-rabbit-herder
Simple herd the rabbit game with the arcade game framework (https://arcade.academy and https://github.com/pvcraven/arcade)

![alt text](https://raw.githubusercontent.com/ryancollingwood/arcade-rabbit-herder/master/resources/static/preview.gif "Rabbit Herder Preview")

## Game Objective

You must herd the the rabbit to the exit in the maze. 
The rabbit will try to keep it's distance from you, so you'll have herd the rabbit where you want it to go!

Rabbits love carrots and will run towards them.
Pickup a carrot before the rabbit you can place the carrots to encourage the rabbit through the maze.
Blue sweets will make both yourself or the rabbit move faster. The red potions will slow down movement.

### Keys
- `↑ ↓ ← →` to move/select
- `SPACE` to place a carrot
- `ESCAPE` to bring up this menu
- `ENTER` to start

# Fun things you could do!
- Modify a level (`resources/level/01/layout.txt`) and see what changes in the game!
- Fork this repo and remix to your hearts content!
- If you have an artistic flair make some sprites for the rabbit and related entities!
- Raise ticket with an idea for additional items!

## Development Objective

Wanted to get familiar with the arcade framework, while also getting familiar with some of the fundamental game design constructs (game loop, acceleration, collision, grid based maps, pathfinding).
While also making something fun and easy :)

Keeping the scope small meant I'd get something complete, and then decide to iterate or move onto something else. I haven't used as much of the aracde framework as I could have (most notably Sprites and it's physic/collision detection offerings).

I opted to have fairly fat classes, rather than going for a factory or a MVC approach. As I wanted the code to be approachable by having the behaviour and states of "things" together as much as possible.

## Future Goals
- [X] Add Menus
- [X] Give the player the player the ability to place carrots
- [X] Implement basic primitive shape sprites
- [ ] Add more levels
- [ ] Add more items

## Stretch Goals
- [ ] Animated sprites 
- [ ] Add hostile NPCs
- [ ] Configuration
- [ ] Sounds
- [ ] Music
- [ ] Use arcade provided collision (pymunk at this point)
- [ ] Build out testing with BDD like steps, I believe a simple game like this ould be a fun candidate to apply automated natural language like testing.
