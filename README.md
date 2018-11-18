# arcade-rabbit-herder
Simple herd the rabbit game with the arcade game framework (https://http://arcade.academy and https://github.com/pvcraven/arcade)

![alt text](https://raw.githubusercontent.com/ryancollingwood/arcade-rabbit-herder/master/static/preview.gif "Rabbit Herder Preview")

## Game Objective

You are the white block and you must herd the green block (the rabbit) to the grey block in the maze.

The rabbit will try to keep a fixed distance away from you, so you'll have to strategicially position yourself to herd the rabbit where you want it to go! Rabbits love carrots (orange blocks) and will run towards them when they are in range.
The blue blocks will make both yourself and the rabbit move faster, similarly the red block will slow down movement.

# Fun things you could do!
- Modify the level (`level.txt`) and see what changes in the game!
- Fork this repo and remix to your hearts content.
- If you have an artisitc flair make some sprites for the rabbit and related entities!

## Development Objective

Wanted to get familiar with the arcade framework, while also getting familiar with some of the fundamental game design constructs (game loop, acceleration, collision, grid based maps, pathfinding).
While also making something fun and easy :)

Keeping the scope small meant I'd get something complete, and then decide to iterate or move onto something else. I haven't used as much of the aracde framework as I could have (most notably Sprites and it's physic/collision detection offerings).

I opted to have fairly fat classes, rather than going for a factory or a MVC approach. As I wanted the code to be approachable by having the behaviour and states of "things" together as much as possible.

## Future Goals
- [ ] Add Menus
- [ ] Add more levels
- [ ] Add more items
- [ ] Give the player the player the ability to place carrots

## Stretch Goals
- [ ] Animated sprites 
- [ ] Add hostile NPCs
- [ ] Configuration
- [ ] Sounds
- [ ] Music
- [ ] Use arcade provided collision (pymunk at this point)
- [ ] Build out testing with BDD like steps, I believe a simple game like this ould be a fun candidate to apply automated natural language like testing.
