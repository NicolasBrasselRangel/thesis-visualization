# thesis-visualization
# Quadratic Reciprocity, Arithmetic Billiards and Parity Checkers

This repository contains the Python code for the simulation/visualization developed as part of my bachelor's thesis in mathematics, titled *"Quadratic Reciprocity, Arithmetic Billiards and Parity Checkers"*. 
The algorithm is from a the article *"Billiards, Checkers, and Quadratic Reciprocity"* by Johan Wästlund.

## Overview

The purpose of this simulation is to visualize an algorithm for solving Parity Checkers in a simple way. The setup is a checkerboard with (black) pebbles on a set of light squares. 
The goal is to place (red) checkers on dark squares such that in the end every light square has an odd number of checkers in its immediate neighborhood if and only if it has a pebble on it.
First, the algorithm makes all squares except the bottom row fulfill the condition and then corrects the missing ones using Arithmetic Billiards.
The (green) path is colored (blue) after a bounce below a square left to do, and at the intersection points of different colored path segments, checkers are placed or removed.
The Legendre Symbol of the dimensions of the outer billiard can be calculated by multiplying the signs of the bounces along the bottom of the rectangle.
If the puzzle consists of pebbles along the bottom row, the Legendre Symbol can also be calculated using the parity of the number of checkers in the solution.

## How to Run

1. Copy the code
2. Install Python and Pygame (`pip install pygame`)
3. Run

## Tutorial

After starting, two coprime positive integers should be specified. These will be the dimensions of the outer billiard. 
Then you can specify whether it should be a puzzle with pebbles only on the bottom row (to calculate the Legendre symbol based on the number of pebbles in the solution).

The controls are then as follows:

- Clicking on the blue square starts the self-solver (repeated clicks trigger the next steps). This is the simplest and
recommended use.

- Left-click to place red tiles on the dark squares.

- Clicking on the green square checks whether the configuration is a solution.

- Clicking on the yellow square starts and pauses the ball.

- Clicking on the red square fast-forwards or resets the trajectory.

- Left-clicking directly under the light squares of the last line sets blue "paint" and colors the trajectory when hitting this point.

- Right-click to mark dark squares (with white circles).

- Pressing the space bar creates a random new puzzle.

- Press "s" to set a puzzle yourself (it is held by pressing again).

## Thesis

You can get the full thesis document upon request.
