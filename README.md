**⚽ 2D Soccer with OpenGL**

- This project is a 2D soccer game developed in Python + OpenGL, focused on introducing computer graphics concepts:
- Drawing primitives (lines, squares, circles).
- Geometric transformations (translation, rotation).
- Basic gameplay mechanics (ball, goals, scoreboard, player movement).
- Sound effects (goal celebration).

**🚀 Features**
- Soccer field drawn with lines and a central circle.
- Ball controlled with the keyboard (arrow keys).
- Ball rebounds off the walls and can be blocked by the goalkeeper.
- Goal detection only when the ball passes exactly between the goalposts → scoreboard updates and play restarts.
- Players automatically positioned and move within their zones:
    - Goalkeeper (G): restricted to the goal area.
    - Defender (Z): moves between the goal and their own half.
    - Midfielder (M): moves between their own half and the opponent’s half.
    - Attacker (A): moves between the opponent’s half and the goal.

- Players automatically chase the ball and “kick” it when in contact.
- Goal sound effect (using playsound).
- Dynamic system → changing the field size automatically updates player movement limits.

**🖥️ Controls**
- WASD → move the ball:
    - W (up)
    - A (down)
    - S (left)
    - D (right).

- Can be combined for diagonal movement.
