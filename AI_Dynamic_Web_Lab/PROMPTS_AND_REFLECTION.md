# Prompts and Reflection

## Prompt 1 — Initial Box Model Lab

Act as a frontend web developer. Using your Canvas tool, Generate an
interactive website that can be used for understanding the CSS Box Model
and its relationship with the display property.

The page must have:

1. Two div elements, 'Box 1' and 'Box 2', so I can see how they interact.
   'Box 1' will be the one we control.
2. The CSS must use different background colors for the content area,
   the padding area, and the margin area of 'Box 1' (e.g., using
   background-clip: content-box). The border should be a solid line.
3. A control panel with:
   - Sliders to control the padding, margin, border-width, and width of Box 1.
   - Labels next to the sliders that show the current pixel value.
   - A Dropdown (select) to change the display property of Box 1 to:
     block, inline-block, and inline.
4. JavaScript that listens to all sliders and the dropdown, and updates
   the CSS properties of Box 1 in real-time.

## Prompt 2 — Refinement

Implement sliders to adjust the margin, padding, and border for each side
(top, right, bottom, left) individually, and add a separate slider for the
corner radius.

## Prompt 3 — Flexbox/Grid Playground

Act as a frontend web developer. Using your Canvas tool, generate an
interactive website that can be used as a playground for CSS Flexbox and Grid.

The page should have:

1. A div element acting as the container.
2. Several div elements inside acting as the items (e.g., 5 items).
3. Dropdown menus (selects) that allow me to change the CSS properties
   of the container.
4. I need to be able to change:
   - display (to switch between block, flex, and grid)
   - flex-direction (row, column)
   - justify-content (flex-start, center, space-between, etc.)
   - align-items (flex-start, center, stretch, etc.)
   - grid-template-columns (e.g., 1fr 1fr, 1fr 1fr 1fr)
5. The JavaScript must update the container's CSS in real-time when I
   change a dropdown.

## Reflection and Synthesis

The interactive labs made CSS concepts easier to understand because I
could immediately observe how changing a property affected the layout.
This was especially useful for the Box Model because padding, margin,
border width, and element width could be changed independently while
watching the result in real time. The display control also made the
difference between block, inline-block, and inline more concrete. For
example, changing an element to display: inline immediately demonstrates
why width behaves differently than it does on a block-level element.
Compared with reading documentation or looking at static diagrams, the
interactive approach provides immediate visual feedback and encourages
experimentation.

Using a sequential refinement prompt was also more effective than placing
every requirement into one very large prompt. The initial prompt produced
a working baseline, while the second prompt concentrated specifically on
adding side-specific margin, padding, border controls, and border radius.
This made the changes easier to understand and verify without disturbing
the rest of the application. The workflow is similar to real-world
software development, where developers first build a functional version,
test it, and then add or refactor features in smaller iterations. AI
therefore becomes part of an iterative development process rather than
simply generating a large final solution in a single step.

## Screenshot placeholders

1. Initial Box Model AI response screenshot
2. Refined Box Model AI response screenshot
3. Flexbox/Grid Playground AI response screenshot

## GitHub Repository Link

Add the link to the task folder in the Artificial Intelligence in Software
Engineering repository here.
