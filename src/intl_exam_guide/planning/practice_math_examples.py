from __future__ import annotations

from intl_exam_guide.planning.subject_profiles import has_terms


def _quadratic_graph_topic(text: str) -> bool:
    return has_terms(text, ["quadratic function", "quadratic functions"]) or has_terms(
        text, ["vertex", "line of symmetry"]
    )


def _kinematics_graph_topic(text: str) -> bool:
    return has_terms(text, ["kinematic", "kinematics", "motion", "displacement", "velocity", "speed"]) and has_terms(
        text, ["graph", "graphs", "gradient", "area under"]
    )


def _short_focus(text: str, limit: int = 80) -> str:
    cleaned = " ".join(text.replace("\n", " ").split()).strip(" .;:")
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def mathematics_specialist_example(
    text: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    if has_terms(text, ["inequality", "inequalities"]):
        return (
            "Solve the inequality x^2 - 5x + 6 > 0 and give the answer as intervals.",
            ["Find the boundary values by solving x^2 - 5x + 6 = 0.", "Use a sign table or number line.", "Choose the intervals where the expression is positive."],
            ["x^2 - 5x + 6 = (x - 2)(x - 3), so the boundary values are x = 2 and x = 3.", "The quadratic is positive outside the two roots.", "Therefore the solution is x < 2 or x > 3.", "Answer: x < 2 or x > 3."],
            ["The inequality sign is answered, not just the equation.", "The boundary values split the number line into intervals.", "The middle interval 2 < x < 3 is rejected."],
        )
    if has_terms(text, ["binomial expansion"]):
        return (
            "Expand (1 + x)^5 up to and including the x^3 term.",
            ["Use binomial coefficients from row 5.", "Write the powers of x in order.", "Stop at the requested term."],
            ["(1 + x)^5 = 1 + 5x + 10x^2 + 10x^3 + 5x^4 + x^5.", "Up to and including x^3 gives 1 + 5x + 10x^2 + 10x^3.", "Answer: 1 + 5x + 10x^2 + 10x^3."],
            ["The coefficients 1, 5, 10, 10 are used in order.", "The powers of x increase by 1 each time.", "Terms beyond x^3 are not included."],
        )
    if has_terms(text, ["trigonometric equations", "simple trigonometric equations"]):
        return (
            "Solve sin x = 1/2 for 0 <= x < 360 degrees.",
            ["Find the reference angle.", "Use the quadrants where sine is positive.", "Keep only solutions inside the interval."],
            ["The reference angle is 30 degrees.", "Sine is positive in quadrants I and II.", "So x = 30 degrees or x = 150 degrees.", "Answer: 30 degrees, 150 degrees."],
            ["Both interval solutions are included.", "The interval endpoint rule is followed.", "The answer solves the equation rather than only converting units."],
        )
    if has_terms(text, ["sine and cosine rules", "sine rule", "cosine rule"]):
        return (
            "In triangle ABC, a = 8 cm, b = 11 cm and angle C = 37 degrees. Use the cosine rule to find side c to 3 significant figures.",
            ["Choose the cosine rule because two sides and the included angle are known.", "Substitute into c^2 = a^2 + b^2 - 2ab cos C.", "Square-root and round appropriately."],
            ["c^2 = 8^2 + 11^2 - 2(8)(11)cos37 degrees.", "c^2 = 185 - 176cos37 degrees.", "c is approximately 6.67.", "Answer: c = 6.67 cm to 3 significant figures."],
            ["The included angle is used.", "The cosine rule is used instead of a right-angle formula.", "The final answer has a length unit."],
        )
    if has_terms(text, ["area of a triangle", "1/2 ab sin", "1/2ab sin"]):
        return (
            "Find the area of a triangle with sides a = 7 cm and b = 10 cm enclosing angle C = 40 degrees.",
            ["Use the non-right-angled triangle area formula.", "Substitute the two sides and included angle.", "Round the area with square units."],
            ["Area = 1/2 ab sin C.", "Area = 1/2 x 7 x 10 x sin40 degrees.", "Area is approximately 22.5.", "Answer: 22.5 cm^2."],
            ["The angle is between the two given sides.", "The sine formula is used for area, not the sine rule.", "The unit is squared."],
        )
    if has_terms(text, ["trigonometrical identities", "trigonometric identities", "tan theta", "sin^2", "cos^2"]):
        return (
            "Use sin^2 x + cos^2 x = 1 to simplify 1 - cos^2 x.",
            ["Choose the identity that contains sin^2 x and cos^2 x.", "Rearrange the identity.", "Replace the expression with the equivalent trig term."],
            ["sin^2 x + cos^2 x = 1.", "Subtract cos^2 x from both sides.", "1 - cos^2 x = sin^2 x.", "Answer: sin^2 x."],
            ["The identity is rearranged, not memorised as a loose phrase.", "Squares stay attached to the trig functions.", "The simplified expression is equivalent for all allowed x."],
        )
    if has_terms(text, ["variable acceleration"]) or (
        has_terms(text, ["displacement", "velocity", "acceleration"])
        and has_terms(text, ["differentiat", "integrat"])
    ):
        if has_terms(text, ["application of calculus"]):
            return (
                "A particle has velocity v(t)=3t^2-4t. Use calculus to find its acceleration at t=2.",
                ["Identify acceleration as dv/dt.", "Differentiate v(t).", "Substitute t=2."],
                ["a(t)=dv/dt=6t-4.", "a(2)=12-4=8.", "Answer: acceleration = 8 m/s^2."],
                ["The calculus operation is chosen from the required quantity.", "Velocity is differentiated once.", "The final value uses the stated time."],
            )
        if has_terms(text, ["restricted to the calculus", "as unit p1"]):
            return (
                "A particle has acceleration a(t)=6t. Given v(0)=2, find v(t) using AS-level integration.",
                ["Integrate acceleration to get velocity.", "Add a constant of integration.", "Use v(0)=2 to find the constant."],
                ["v(t)=integral 6t dt = 3t^2 + C.", "v(0)=C=2.", "Answer: v(t)=3t^2+2."],
                ["Only basic integration is needed.", "The initial condition fixes C.", "The result is a velocity function."],
            )
        return (
            "A particle has displacement s(t) = t^3 - 6t^2 + 9t metres. Find v(t), a(t), and the velocity at t = 2.",
            ["Differentiate displacement to get velocity.", "Differentiate velocity to get acceleration.", "Substitute t = 2 into v(t)."],
            ["v(t) = ds/dt = 3t^2 - 12t + 9.", "a(t) = dv/dt = 6t - 12.", "v(2) = 3(2)^2 - 12(2) + 9 = -3.", "Answer: v(t)=3t^2-12t+9, a(t)=6t-12, and v(2)=-3 m/s."],
            ["This is calculus, not constant-acceleration SUVAT.", "Velocity is the derivative of displacement.", "Acceleration is the derivative of velocity."],
        )
    if has_terms(text, ["relative frequencies", "equally likely outcomes", "assigning probabilities", "probability"]) and not has_terms(
        text, ["random variable", "random variables", "discrete random"]
    ):
        if has_terms(text, ["relative frequencies"]):
            return (
                "A coin is tossed 50 times and lands heads 31 times. Estimate the probability of heads from the relative frequency.",
                ["Use frequency divided by total trials.", "Write the estimate as a decimal or fraction.", "State that it is an estimate."],
                ["Estimated probability = 31/50.", "31/50 = 0.62.", "Answer: estimated probability of heads is 0.62."],
                ["Relative frequency uses observed results.", "The answer is an estimate, not an exact value.", "The total number of trials is 50."],
            )
        if has_terms(text, ["addition law"]):
            return (
                "Events A and B have P(A)=0.4, P(B)=0.3 and P(A and B)=0.1. Find P(A or B).",
                ["Use the addition law.", "Subtract the overlap once.", "State the union probability."],
                ["P(A or B)=P(A)+P(B)-P(A and B).", "P(A or B)=0.4+0.3-0.1.", "Answer: 0.6."],
                ["The overlap is not double-counted.", "The addition law is named.", "The answer is between 0 and 1."],
            )
        if has_terms(text, ["multiplication law", "conditional probability"]):
            return (
                "P(A)=0.5 and P(B|A)=0.6. Find P(A and B).",
                ["Use the multiplication law.", "Multiply P(A) by P(B|A).", "State the joint probability."],
                ["P(A and B)=P(A)P(B|A).", "P(A and B)=0.5 x 0.6.", "Answer: 0.3."],
                ["The conditional probability is used in the correct direction.", "The result is a joint probability.", "The answer is between 0 and 1."],
            )
        if has_terms(text, ["application of probability laws"]):
            return (
                "In a class, P(studies maths)=0.7, P(studies physics)=0.4 and P(studies both)=0.25. Find the probability a student studies maths or physics.",
                ["Choose the appropriate probability law.", "Add the two probabilities.", "Subtract the overlap."],
                ["P(M or P)=P(M)+P(P)-P(M and P).", "P(M or P)=0.7+0.4-0.25.", "Answer: 0.85."],
                ["The context is translated into events.", "The overlap is subtracted.", "The probability is not greater than 1."],
            )
        return (
            "A fair die is rolled once. Find the probability of getting a number greater than 4.",
            ["Count the favourable outcomes.", "Count all equally likely outcomes.", "Write the probability as a fraction."],
            ["Numbers greater than 4 are 5 and 6.", "There are 2 favourable outcomes out of 6 equally likely outcomes.", "P(number > 4) = 2/6 = 1/3.", "Answer: 1/3."],
            ["Equal likelihood means simple counting works.", "The probability is reduced to simplest form.", "The sample space has 6 outcomes."],
        )
    if has_terms(text, ["using algebraic methods", "equal roots", "distinct real roots", "no real roots"]):
        return (
            "Two curves intersect when x^2 - 4x + 5 = 0. Use the discriminant to decide whether the curves meet.",
            ["Write the intersection equation.", "Calculate the discriminant.", "Interpret the sign of the discriminant in context."],
            ["For x^2 - 4x + 5 = 0, a=1, b=-4, c=5.", "b^2 - 4ac = 16 - 20 = -4.", "The discriminant is negative.", "Answer: there are no real intersections."],
            ["The discriminant links algebra to graph intersections.", "No real roots means no real intersection points.", "The conclusion is stated in context."],
        )
    if has_terms(text, ["geometrical interpretation", "algebraic solution"]):
        return (
            "The equation x^2 - 4x + 4 = 0 comes from two graphs meeting. Use the repeated root to describe the graph relationship.",
            ["Solve or identify the root structure.", "Connect a repeated root to a single contact point.", "State the graphical interpretation."],
            ["x^2 - 4x + 4 = (x - 2)^2.", "There is one repeated root, x = 2.", "A repeated root means the graphs touch at one point.", "Answer: the graphs are tangent or just touch at the intersection."],
            ["The root count is interpreted geometrically.", "A repeated root is not two crossings.", "The answer describes the graph relationship."],
        )
    if has_terms(text, ["simultaneous equations"]):
        return (
            "Solve the simultaneous equations y = x + 1 and y = x^2 - 5.",
            ["Set the two expressions for y equal.", "Solve the resulting quadratic.", "Substitute each x-value into either equation."],
            ["x + 1 = x^2 - 5, so x^2 - x - 6 = 0.", "(x - 3)(x + 2) = 0, so x = 3 or x = -2.", "Then y = 4 or y = -1.", "Answer: (3, 4) and (-2, -1)."],
            ["Both coordinates are found.", "The equations are solved together.", "The answers can be checked in both equations."],
        )
    if has_terms(text, ["translation of circles", "translated circle"]):
        return (
            "The circle x^2 + y^2 = 9 is translated 4 units right and 2 units down. Write the new equation.",
            ["Move the centre by the translation vector.", "Keep the radius the same.", "Write the completed-square form."],
            ["The original centre is (0,0) and radius is 3.", "After translation the centre is (4,-2).", "New equation: (x-4)^2 + (y+2)^2 = 9.", "Answer: (x-4)^2 + (y+2)^2 = 9."],
            ["A translation changes the centre, not the radius.", "The y-coordinate sign changes correctly.", "The final equation matches the new centre."],
        )
    if has_terms(text, ["surd", "surds", "rationalisation"]):
        return (
            "Simplify sqrt(72) + sqrt(18), then rationalise 5/sqrt(2).",
            ["Write each surd using square factors.", "Collect like surds.", "Multiply numerator and denominator by sqrt(2)."],
            ["sqrt(72) = sqrt(36 x 2) = 6sqrt(2).", "sqrt(18) = sqrt(9 x 2) = 3sqrt(2), so the sum is 9sqrt(2).", "5/sqrt(2) = 5sqrt(2)/2.", "Answer: 9sqrt(2) and 5sqrt(2)/2."],
            ["Square factors are taken outside the root.", "Only like surds are combined.", "The denominator is rational after rationalising."],
        )
    if has_terms(text, ["exponential", "logarithm", "logarithms"]):
        if has_terms(text, ["graph"]):
            return (
                "For y = 2^x, state the y-intercept and describe what happens as x becomes very negative.",
                ["Substitute x = 0 for the y-intercept.", "Use the shape of an exponential graph.", "State the asymptote behaviour."],
                ["When x = 0, y = 2^0 = 1.", "As x becomes very negative, 2^x gets closer to 0 but stays positive.", "Answer: y-intercept (0, 1); the graph approaches y = 0."],
                ["The intercept is found from x = 0.", "The graph stays above the x-axis.", "The horizontal asymptote is described in words."],
            )
        return (
            "Solve 3^x = 81, then write the result using logarithm notation.",
            ["Write 81 as a power of 3.", "Equate the powers.", "Connect the answer to log notation."],
            ["81 = 3^4.", "So 3^x = 3^4 gives x = 4.", "In log form, log_3 81 = 4.", "Answer: x = 4."],
            ["The base is 3.", "The logarithm statement matches the exponential statement.", "The answer is checked by substitution."],
        )
    if has_terms(text, ["indices", "index", "rational exponent", "rational exponents"]):
        return (
            "Simplify a^(3/2) x a^(1/2), then write a^(1/2) as a surd.",
            ["Use the index law for multiplying powers with the same base.", "Add the exponents.", "Translate the one-half power into surd notation."],
            ["a^(3/2) x a^(1/2) = a^(3/2 + 1/2).", "3/2 + 1/2 = 4/2 = 2.", "So the product is a^2.", "a^(1/2) = sqrt(a)."],
            ["The base stays as a.", "Only exponents are added for multiplication.", "The rational exponent is converted to the matching root."],
        )
    if has_terms(text, ["discriminant"]):
        return (
            "Use the discriminant to decide how many real roots x^2 - 4x + 5 = 0 has.",
            ["Identify a, b and c.", "Calculate b^2 - 4ac.", "Use the sign of the discriminant."],
            ["Here a=1, b=-4 and c=5.", "b^2 - 4ac = (-4)^2 - 4(1)(5) = 16 - 20 = -4.", "The discriminant is negative.", "Answer: the equation has no real roots."],
            ["The negative b value is squared correctly.", "A negative discriminant means no real roots.", "The conclusion is about roots, not turning points."],
        )
    if has_terms(text, ["quadratic equation", "quadratic equations"]) and not has_terms(
        text, ["inequality", "inequalities", "discriminant", "graph", "graphs", "function", "functions"]
    ):
        return (
            "Solve x^2 - 7x + 10 = 0 by factorising.",
            ["Find two numbers that multiply to 10 and add to -7.", "Write the quadratic as two factors.", "Set each factor equal to zero."],
            ["x^2 - 7x + 10 = (x - 5)(x - 2).", "So x - 5 = 0 or x - 2 = 0.", "x = 5 or x = 2.", "Answer: x = 2 or x = 5."],
            ["Both roots are included.", "The factor signs produce -7x.", "The answer is solving an equation, not an inequality."],
        )
    if has_terms(text, ["completing the square", "complete the square"]):
        if has_terms(text, ["factorisation", "quadratic formula"]):
            return (
                "Solve x^2 + 6x + 2 = 0 by completing the square, then state why the quadratic formula would give the same roots.",
                ["Complete the square.", "Set the completed-square expression equal to zero.", "Connect the rearranged form to the quadratic formula method."],
                ["x^2 + 6x + 2 = (x + 3)^2 - 7.", "So (x + 3)^2 = 7.", "x = -3 +/- sqrt(7).", "Answer: x = -3 +/- sqrt(7); the quadratic formula is the same algebra rearranged."],
                ["The square is completed before solving.", "Both plus and minus roots are included.", "The method matches a quadratic-equation topic."],
            )
        return (
            "Write x^2 + 6x - 1 in completed-square form.",
            ["Halve the coefficient of x.", "Add and subtract the square of that half.", "Simplify the constant term."],
            ["Half of 6 is 3.", "x^2 + 6x - 1 = (x+3)^2 - 9 - 1.", "So x^2 + 6x - 1 = (x+3)^2 - 10.", "Answer: (x+3)^2 - 10."],
            ["The bracket uses half the x coefficient.", "The extra 9 is subtracted back.", "Expanding the answer checks it."],
        )
    if has_terms(text, ["factorisation", "factorization"]) and has_terms(text, ["quadratic", "quadratics"]):
        return (
            "Factorise 2x^2 + x - 6.",
            ["Find two terms whose product matches 2x^2 and -6.", "Split the middle term.", "Factorise by grouping."],
            ["2x^2 + x - 6 = 2x^2 + 4x - 3x - 6.", "Group: 2x(x+2) - 3(x+2).", "Take out the common bracket.", "Answer: (2x-3)(x+2)."],
            ["Expanding gives 2x^2 + x - 6.", "The signs in the brackets are correct.", "Both factors are included."],
        )
    if has_terms(text, ["sine", "cosine", "tangent", "trigonometry", "trigonometric"]) and has_terms(
        text, ["graphs", "symmetries", "periodicity", "period"]
    ):
        return (
            "For y = sin x on 0 <= x <= 360 degrees, state the period and the x-values where y = 0.",
            ["Use the standard sine graph.", "Read one full cycle.", "List the zeros in the interval."],
            ["The sine graph repeats every 360 degrees, so the period is 360 degrees.", "On 0 <= x <= 360 degrees, sin x = 0 at x = 0, 180 and 360 degrees.", "Answer: period 360 degrees; zeros at 0, 180 and 360 degrees."],
            ["The graph property is trigonometric, not quadratic.", "Both endpoints are included.", "The answer is tied to the stated interval."],
        )
    if "|r|<1" in text.replace(" ", "") or has_terms(text, ["convergent"]):
        if has_terms(text, ["sum to infinity"]):
            return (
                "A geometric series has first term 5 and common ratio 0.4. Find the sum to infinity.",
                ["Check that |r|<1.", "Use S_infinity = a/(1-r).", "Substitute a and r."],
                ["Here |r| = 0.4 < 1, so the sum to infinity exists.", "S_infinity = 5/(1 - 0.4).", "S_infinity = 5/0.6 = 25/3.", "Answer: 25/3."],
                ["The convergence condition is checked.", "The first term is used as a.", "The answer is for an infinite sum."],
            )
        return (
            "A geometric series has common ratio r = -0.6. Use |r|<1 to decide whether it is convergent.",
            ["Find the absolute value of the common ratio.", "Compare it with 1.", "State the convergence conclusion."],
            ["Here |r| = |-0.6| = 0.6.", "Since 0.6 < 1, the condition |r|<1 is satisfied.", "Answer: the geometric series is convergent."],
            ["The absolute value of r is used.", "The comparison is with 1.", "The conclusion names the geometric-series condition."],
        )
    if _kinematics_graph_topic(text):
        if has_terms(text, ["sketching", "interpreting"]):
            return (
                "A particle moves with constant positive velocity for 4 seconds, then rests for 2 seconds. Describe the shape of its displacement-time graph.",
                ["Use gradient on a displacement-time graph to represent velocity.", "Constant positive velocity gives a straight rising line.", "Rest gives a horizontal line."],
                ["From 0 to 4 seconds, displacement increases at a constant rate, so the graph is a straight rising line.", "From 4 to 6 seconds, the particle rests, so displacement is constant.", "Answer: rising straight line followed by a horizontal segment."],
                ["The axes are displacement and time.", "Rest is horizontal on a displacement-time graph.", "The sketch matches the motion story."],
            )
        return (
            "A velocity-time graph is a straight line from (0, 2) to (4, 10). Find the acceleration and the displacement in the first 4 seconds.",
            ["Use the gradient of a velocity-time graph for acceleration.", "Use the area under the graph for displacement.", "State units."],
            ["Acceleration = (10 - 2)/(4 - 0) = 2 m/s^2.", "Displacement is the area of the trapezium under the graph.", "Area = 1/2 x (2 + 10) x 4 = 24.", "Answer: acceleration 2 m/s^2; displacement 24 m."],
            ["The graph is velocity-time, not displacement-time.", "Gradient gives acceleration.", "Area under velocity-time gives displacement."],
        )
    if has_terms(text, ["intersection points of graphs", "graphs of functions to solve equations"]):
        if has_terms(text, ["vice versa", "interpreting the solutions"]):
            return (
                "A graph shows intersections at x = -1 and x = 3. Write the corresponding solution set for the equation f(x)=g(x).",
                ["Read the x-coordinates of the intersection points.", "Translate intersections into equation solutions.", "State the solution set."],
                ["Solutions of f(x)=g(x) occur where the graphs have equal y-values.", "The intersections have x-coordinates -1 and 3.", "Answer: x = -1 or x = 3."],
                ["Only the x-values are needed for the equation solution.", "The graph reading is translated back into algebra.", "Both intersections are included."],
            )
        return (
            "Find the intersection points of y = x^2 and y = x + 2.",
            ["Set the two expressions for y equal.", "Solve the resulting quadratic.", "Substitute each x-value to find y."],
            ["x^2 = x + 2, so x^2 - x - 2 = 0.", "(x - 2)(x + 1) = 0, so x = 2 or x = -1.", "When x = 2, y = 4; when x = -1, y = 1.", "Answer: (2, 4) and (-1, 1)."],
            ["Intersection means the y-values are equal.", "Both coordinates are given.", "The algebra is interpreted as graph intersections."],
        )
    if _quadratic_graph_topic(text):
        return (
            "For y = (x - 3)^2 + 2, state the vertex and line of symmetry.",
            ["Recognise completed-square form.", "Read the horizontal shift carefully.", "The line of symmetry passes through the vertex."],
            ["The minimum point is at x = 3.", "The y-value there is 2.", "So the vertex is (3, 2).", "Answer: vertex (3, 2), line of symmetry x = 3."],
            ["The sign inside the bracket reverses for the x-coordinate.", "The line of symmetry is vertical.", "The answer describes the graph, not just the equation."],
        )
    if has_terms(text, ["divided", "division"]) and has_terms(text, ["polynomial", "polynomials"]):
        if has_terms(text, ["remainder is", "factor and vice versa"]):
            return (
                "For f(x)=2x^3-3x+5, find the remainder when f(x) is divided by x-2.",
                ["Use the Remainder Theorem.", "Substitute x = 2 into f(x).", "State the result as the remainder."],
                ["f(2)=2(2)^3-3(2)+5.", "f(2)=16-6+5=15.", "The remainder is f(2).", "Answer: remainder 15."],
                ["The divisor x-2 gives x=2.", "No full division is needed.", "The value is the remainder, not the quotient."],
            )
        return (
            "Find the remainder when f(x)=x^3-4x^2+x+6 is divided by x-2.",
            ["Use the Remainder Theorem.", "Evaluate f(2).", "State the remainder."],
            ["For division by x-2, use x=2.", "f(2)=8-16+2+6.", "f(2)=0.", "Answer: the remainder is 0."],
            ["The divisor x-2 gives x=2.", "The value of f(2) is the remainder.", "A zero remainder means exact division."],
        )
    if has_terms(text, ["factor theorem", "remainder theorem"]):
        if has_terms(text, ["use of the remainder theorem and the factor theorem"]):
            return (
                "For f(x)=x^3-x^2-4x+4, use the Remainder Theorem and Factor Theorem to test x-1 and x-2.",
                ["Evaluate f(1) and f(2).", "Interpret each value as a remainder.", "A zero remainder identifies a factor."],
                ["f(1)=1-1-4+4=0, so x-1 is a factor.", "f(2)=8-4-8+4=0, so x-2 is also a factor.", "Both tested divisors give zero remainders.", "Answer: x-1 and x-2 are factors."],
                ["Each divisor gives its own test value.", "Zero means factor.", "The theorem is used rather than guessed from a graph."],
            )
        if has_terms(text, ["application"]):
            return (
                "For f(x)=x^3+2x^2-x-2, use the Factor Theorem to check whether x+2 is a factor.",
                ["Use x+2 = 0 to find the test value.", "Evaluate f(-2).", "Interpret a zero remainder."],
                ["For x+2, test x = -2.", "f(-2)=-8+8+2-2.", "f(-2)=0.", "Therefore x+2 is a factor of f(x)."],
                ["The test value is -2.", "A zero value means factor.", "The conclusion names x+2."],
            )
        return (
            "For f(x)=x^3-4x^2+x+6, use the Factor Theorem to check whether x-2 is a factor.",
            ["Use x-2 = 0 to find the test value.", "Evaluate f(2).", "Interpret a zero remainder."],
            ["For x-2, test x = 2.", "f(2)=8-16+2+6.", "f(2)=0.", "Therefore x-2 is a factor of f(x)."],
            ["The test value has the correct sign.", "A zero value means factor, not just root by guesswork.", "The conclusion names the factor."],
        )
    if has_terms(text, ["circle", "circles"]):
        if has_terms(text, ["tangent", "normal"]):
            return (
                "For the circle x^2 + y^2 = 25, point P(3, 4) lies on the circle. Find the gradient of the tangent at P.",
                ["Find the gradient of the radius OP.", "Use the perpendicular-gradient rule for the tangent.", "State the tangent gradient."],
                ["The radius from (0,0) to (3,4) has gradient 4/3.", "The tangent is perpendicular to the radius.", "So the tangent gradient is -3/4.", "Answer: -3/4."],
                ["The radius and tangent are perpendicular.", "Use the negative reciprocal.", "The point lies on the circle."],
            )
        return (
            "Write the centre and radius of (x-3)^2 + (y+2)^2 = 25.",
            ["Compare with (x-a)^2 + (y-b)^2 = r^2.", "Read the centre signs carefully.", "Square-root the right-hand side."],
            ["The centre is (3, -2).", "r^2 = 25.", "r = 5.", "Answer: centre (3, -2), radius 5."],
            ["The y-coordinate sign is not copied as +2.", "The radius is positive.", "The equation is in completed-square circle form."],
        )
    if has_terms(text, ["sine, cosine and tangent functions", "sine cosine and tangent functions"]):
        return (
            "In a right-angled triangle, the side opposite angle A is 5 and the hypotenuse is 13. Find sin A.",
            ["Use sine as opposite over hypotenuse.", "Substitute the given side lengths.", "Simplify if possible."],
            ["sin A = opposite / hypotenuse.", "sin A = 5/13.", "Answer: 5/13."],
            ["The correct trig ratio is selected.", "The hypotenuse is the denominator.", "No radian conversion is needed."],
        )
    if has_terms(text, ["trigonometry", "radian", "radians", "sine", "cosine"]):
        return (
            "Convert pi/3 radians to degrees, then find the exact value of sin(pi/3).",
            ["Use pi radians = 180 degrees.", "Convert the angle.", "Use the exact trig value."],
            ["pi/3 radians = 180/3 degrees.", "So the angle is 60 degrees.", "sin(pi/3)=sin 60 degrees.", "Answer: sqrt(3)/2."],
            ["Radian conversion uses pi radians = 180 degrees.", "The exact value is not rounded.", "The angle is in the first quadrant."],
        )
    if has_terms(text, ["sequence", "sequences", "series", "arithmetic", "geometric"]):
        if has_terms(text, ["x_(n+1)", "recurrence", "simple relation"]):
            return (
                "A sequence is defined by x_1 = 2 and x_(n+1) = 3x_n - 1. Find x_2 and x_3.",
                ["Use the recurrence relation one step at a time.", "Substitute x_1 to find x_2.", "Substitute x_2 to find x_3."],
                ["x_2 = 3(2) - 1 = 5.", "x_3 = 3(5) - 1 = 14.", "Answer: x_2 = 5 and x_3 = 14."],
                ["Each term uses the previous term.", "The starting value is used first.", "Do not treat n as the term value."],
            )
        if has_terms(text, ["finite geometric series"]):
            return (
                "A geometric series has first term 3 and common ratio 2. Find the sum of the first 5 terms.",
                ["Use the finite geometric-series formula.", "Substitute a=3, r=2, n=5.", "Calculate the finite sum."],
                ["S_5 = a(r^5 - 1)/(r - 1).", "S_5 = 3(2^5 - 1)/(2 - 1).", "S_5 = 3(31) = 93.", "Answer: 93."],
                ["This is finite, not sum to infinity.", "The common ratio is used as r.", "The number of terms is 5."],
            )
        if has_terms(text, ["arithmetic series", "natural numbers"]):
            return (
                "Find the sum of the first 20 natural numbers.",
                ["Use the arithmetic-series formula.", "Substitute n=20.", "Simplify the product."],
                ["S_n = n(n+1)/2 for the first n natural numbers.", "S_20 = 20(21)/2.", "Answer: 210."],
                ["The formula is for 1 + 2 + ... + n.", "n is 20.", "The result is a sum, not the 20th term."],
            )
        return (
            "An arithmetic sequence has first term 7 and common difference 4. Find the 12th term and the sum of the first 12 terms.",
            ["Use a_n = a + (n-1)d.", "Substitute n = 12.", "Use the arithmetic-series sum formula."],
            ["a_12 = 7 + 11 x 4 = 51.", "S_12 = 12/2 x (7 + 51).", "S_12 = 6 x 58 = 348.", "Answer: 12th term 51; sum 348."],
            ["n-1 is used in the nth-term formula.", "The first and last terms are used in the sum.", "The answer separates term and sum."],
        )
    if has_terms(text, ["coordinate", "coordinates", "straight line", "gradient", "perpendicular"]) and not has_terms(
        text,
        [
            "acceleration",
            "derivative",
            "differentiation",
            "displacement",
            "motion",
            "speed",
            "stationary",
            "tangent",
            "velocity",
        ],
    ):
        if has_terms(text, ["parallel"]):
            return (
                "Line l has equation y = 2x + 5. Find the gradient of a line parallel to l.",
                ["Recall that parallel lines have equal gradients.", "Read the gradient from y = mx + c.", "State the matching gradient."],
                ["For y = 2x + 5, the gradient is 2.", "A parallel line has the same gradient.", "Answer: gradient 2."],
                ["The y-intercept is not needed.", "Parallel means same gradient.", "The answer is a gradient, not an equation."],
            )
        if has_terms(text, ["perpendicular"]):
            return (
                "Line l has gradient 4. Find the gradient of a line perpendicular to l.",
                ["Use m1 x m2 = -1 for perpendicular lines.", "Substitute m1 = 4.", "Solve for m2."],
                ["4m2 = -1.", "m2 = -1/4.", "Answer: the perpendicular gradient is -1/4."],
                ["The gradients multiply to -1.", "The sign changes.", "The answer is the negative reciprocal."],
            )
        if has_terms(text, ["intersection of a straight line and a curve"]):
            return (
                "Find where the line y = x + 1 meets the curve y = x^2 - 5.",
                ["Set the two expressions for y equal.", "Solve the resulting quadratic.", "Substitute back to find y-values."],
                ["x + 1 = x^2 - 5, so x^2 - x - 6 = 0.", "(x - 3)(x + 2)=0, so x=3 or x=-2.", "The points are (3,4) and (-2,-1).", "Answer: (3,4), (-2,-1)."],
                ["Both intersection points are given.", "The line and curve equations are both used.", "The answer includes coordinates."],
            )
        return (
            "Find the equation of the line through (2, 5) with gradient 3.",
            ["Start with y = mx + c.", "Substitute the gradient.", "Use the point to find c."],
            ["y = 3x + c.", "Using (2, 5): 5 = 3(2) + c.", "c = -1.", "Answer: y = 3x - 1."],
            ["The gradient is the coefficient of x.", "The point is substituted into the line equation.", "The final equation is in terms of x and y."],
        )
    if has_terms(text, ["indefinite integration as the reverse of differentiation"]):
        return (
            "Differentiate 2x^3 - 5x + C to show why it is a possible indefinite integral of 6x^2 - 5.",
            ["Differentiate the proposed antiderivative.", "Compare it with the integrand.", "Explain the role of C."],
            ["d/dx(2x^3 - 5x + C) = 6x^2 - 5.", "This matches the integrand.", "C differentiates to 0, so any constant is possible.", "Answer: 2x^3 - 5x + C is an indefinite integral."],
            ["Integration reverses differentiation.", "The constant C is explained.", "The check is done by differentiating."],
        )
    if has_terms(text, ["derivative", "differentiation", "tangent", "gradient", "stationary", "second order"]):
        if has_terms(text, ["notation", "notations", "dy/dx", "f'"]):
            return (
                "If f(x)=x^3, write f'(x) and dy/dx for y=x^3.",
                ["Use derivative notation for f.", "Use dy/dx notation for y.", "Differentiate x^3."],
                ["f'(x)=3x^2.", "For y=x^3, dy/dx=3x^2.", "Answer: f'(x)=3x^2 and dy/dx=3x^2."],
                ["Both notations mean the derivative in this context.", "The power rule is applied once.", "The notation matches the function name."],
            )
        if has_terms(text, ["second order"]):
            return (
                "For y = x^3 - 3x^2 + 2, find d2y/dx2.",
                ["Differentiate once to find dy/dx.", "Differentiate again.", "State the second derivative."],
                ["dy/dx = 3x^2 - 6x.", "d2y/dx2 = 6x - 6.", "Answer: d2y/dx2 = 6x - 6."],
                ["The function is differentiated twice.", "The notation means second derivative.", "The final expression is not set equal to zero unless asked."],
            )
        if has_terms(text, ["general appreciation", "interpreting it"]):
            return (
                "A graph has gradient 5 at x = 2. Interpret this derivative value in words.",
                ["Connect derivative to local rate of change.", "Use the x-value as the point of interpretation.", "State what the sign and size mean."],
                ["The derivative at x = 2 is the gradient of the tangent there.", "A value of 5 means y is increasing at 5 units of y per unit of x at that point.", "Answer: the local rate of change is 5."],
                ["This is interpretation, not another differentiation calculation.", "The derivative is local to the point.", "The positive value means increasing."],
            )
        if has_terms(text, ["x^n", "rational number"]):
            return (
                "Differentiate y = x^(1/2) + x^(-2).",
                ["Use the power rule for each rational power.", "Reduce each exponent by 1.", "Keep negative powers in exact form."],
                ["dy/dx = (1/2)x^(-1/2) - 2x^(-3).", "Answer: dy/dx = 1/(2sqrt(x)) - 2/x^3."],
                ["The fractional power is differentiated by the same rule.", "The negative exponent is handled carefully.", "The expression is exact."],
            )
        if has_terms(text, ["polynomials"]):
            return (
                "Differentiate y = 4x^3 - 5x^2 + 7 with respect to x.",
                ["Apply the power rule to each term.", "The constant differentiates to zero.", "Collect the derivative terms."],
                ["dy/dx = 12x^2 - 10x.", "The derivative of 7 is 0.", "Answer: dy/dx = 12x^2 - 10x."],
                ["Each power is reduced by 1.", "Coefficients are multiplied by the old power.", "Constants disappear."],
            )
        if has_terms(text, ["maxima", "minima", "stationary", "increasing", "decreasing"]):
            return (
                "For y = x^2 - 6x + 8, find the stationary point.",
                ["Differentiate the function.", "Set dy/dx = 0.", "Substitute the x-value back into y."],
                ["dy/dx = 2x - 6.", "2x - 6 = 0 gives x = 3.", "y = 3^2 - 6(3) + 8 = -1.", "Answer: stationary point (3, -1)."],
                ["A stationary point has zero gradient.", "The y-coordinate is found by substitution.", "The answer is a point."],
            )
        if has_terms(text, ["normal"]):
            return (
                "A curve has tangent gradient 2 at point P. Find the gradient of the normal at P.",
                ["Use the perpendicular-gradient rule.", "The tangent and normal gradients multiply to -1.", "Solve for the normal gradient."],
                ["2 x m_normal = -1.", "m_normal = -1/2.", "Answer: normal gradient -1/2."],
                ["The normal is perpendicular to the tangent.", "Use negative reciprocal.", "The answer is a gradient."],
            )
        return (
            "For y = 3x^2 - 4x + 1, find dy/dx and the gradient of the tangent when x = 2.",
            ["Differentiate term by term.", "Substitute x = 2 into the derivative.", "State the gradient clearly."],
            ["dy/dx = 6x - 4.", "When x = 2, dy/dx = 6(2) - 4.", "The gradient is 8.", "Answer: dy/dx = 6x - 4; tangent gradient = 8."],
            ["The constant differentiates to 0.", "The x-value is substituted after differentiating.", "The gradient is a number."],
        )
    if has_terms(text, ["trapezium"]):
        return (
            "Use the trapezium rule with step width 1 to estimate the area under y = x^2 from x = 0 to x = 4.",
            ["List the ordinates at x = 0, 1, 2, 3 and 4.", "Substitute them into h/2(first + last + 2 x middle sum).", "State that the result is an estimate."],
            ["The ordinates are 0, 1, 4, 9 and 16.", "With h = 1, estimate = 1/2[0 + 16 + 2(1 + 4 + 9)].", "Estimate = 1/2[16 + 28] = 22.", "Answer: the estimated area is 22 square units."],
            ["The internal ordinates are doubled.", "The width h is included.", "The answer is described as an estimate, not an exact integral."],
        )
    if has_terms(text, ["integration", "integral", "area under"]):
        if has_terms(text, ["interpretation of the definite integral as the area under a curve"]):
            return (
                "Explain what the definite integral of a positive function from x = 1 to x = 4 represents on its graph.",
                ["Identify the interval on the x-axis.", "Connect the integral to area under the curve.", "State the condition about positivity."],
                ["The limits x = 1 and x = 4 mark the horizontal interval.", "For a positive function, the definite integral gives the area between the curve and the x-axis.", "Answer: it represents that area over 1 <= x <= 4."],
                ["This is interpretation, not just calculation.", "The area is tied to the limits.", "The positivity condition avoids signed-area confusion."],
            )
        if has_terms(text, ["definite integral", "evaluation of definite"]):
            return (
                "Evaluate the definite integral of 3x^2 from x = 1 to x = 3.",
                ["Find an antiderivative.", "Substitute the upper limit.", "Subtract the lower-limit value."],
                ["An antiderivative of 3x^2 is x^3.", "At x=3, x^3=27; at x=1, x^3=1.", "27 - 1 = 26.", "Answer: 26."],
                ["Upper minus lower is used.", "No constant C is needed for a definite integral.", "The antiderivative differentiates back to 3x^2."],
            )
        if has_terms(text, ["x^n", "rational number"]):
            return (
                "Find the indefinite integral of x^(1/2) + 2x^3 with respect to x.",
                ["Increase each power by 1.", "Divide by the new power.", "Add the constant of integration."],
                ["Integral of x^(1/2) is x^(3/2)/(3/2) = (2/3)x^(3/2).", "Integral of 2x^3 is (1/2)x^4.", "Answer: (2/3)x^(3/2) + (1/2)x^4 + C."],
                ["The fractional power rule is used.", "The constant C is included.", "The excluded n=-1 case is avoided."],
            )
        if has_terms(text, ["area", "curve", "x-axis"]):
            return (
                "Find the area under y = 2x from x = 1 to x = 4.",
                ["Set up the definite integral.", "Find an antiderivative.", "Subtract lower limit from upper limit."],
                ["Area = integral from 1 to 4 of 2x dx.", "An antiderivative of 2x is x^2.", "Area = 4^2 - 1^2 = 16 - 1.", "Answer: 15 square units."],
                ["The limits are used in the correct order.", "The antiderivative is checked by differentiating.", "Area is positive."],
            )
        return (
            "Find the indefinite integral of 6x^2 - 4x with respect to x.",
            ["Increase each power by 1.", "Divide by the new power.", "Add the constant of integration."],
            ["The integral of 6x^2 is 2x^3.", "The integral of -4x is -2x^2.", "Add the constant C.", "Answer: 2x^3 - 2x^2 + C."],
            ["The power rule is reversed.", "The constant C is included.", "Differentiating the answer checks the integrand."],
        )
    if has_terms(text, ["logarithm", "logarithms", "exponential", "exponentials"]):
        return (
            "Solve 3^x = 81, then write the result using logarithm notation.",
            ["Write 81 as a power of 3.", "Equate the powers.", "Connect the answer to log notation."],
            ["81 = 3^4.", "So 3^x = 3^4 gives x = 4.", "In log form, log_3 81 = 4.", "Answer: x = 4."],
            ["The base is 3.", "The logarithm statement matches the exponential statement.", "The answer is checked by substitution."],
        )
    if has_terms(text, ["binomial", "bernoulli"]):
        if has_terms(text, ["deductions of np", "corresponding values"]):
            return (
                "A Bernoulli random variable has P(success)=p. Use this to state the mean and variance of X ~ B(n,p).",
                ["Recall the Bernoulli mean and variance.", "Scale from one trial to n independent trials.", "State the binomial results."],
                ["For one Bernoulli trial, mean is p and variance is p(1-p).", "For n independent trials, the binomial mean is np.", "The binomial variance is np(1-p).", "Answer: E(X)=np, Var(X)=np(1-p)."],
                ["The result is derived from repeated Bernoulli trials.", "The variance includes 1-p.", "No numerical substitution is needed."],
            )
        if has_terms(text, ["conditions for application"]):
            return (
                "A trial records whether a component is defective. State why this can be modelled as a Bernoulli trial.",
                ["Check the number of outcomes.", "Identify success/failure.", "State the constant probability condition."],
                ["There are two outcomes: defective or not defective.", "One outcome can be called success.", "If the success probability is fixed for the trial, it is Bernoulli.", "Answer: two outcomes with fixed success probability."],
                ["The model condition is stated, not calculated.", "Success is defined clearly.", "Only one trial is being described."],
            )
        if has_terms(text, ["calculation of probabilities", "formula and tables"]):
            return (
                "Let X ~ B(8, 0.25). Write the formula expression for P(X=3).",
                ["Use the binomial probability formula.", "Substitute n=8, p=0.25 and x=3.", "Leave as an exact expression if no calculator is required."],
                ["P(X=3)=C(8,3)(0.25)^3(0.75)^5.", "This is the formula expression for exactly 3 successes.", "Answer: C(8,3)(0.25)^3(0.75)^5."],
                ["The success power is 3.", "The failure power is 5.", "The combination term counts arrangements."],
            )
        if not has_terms(text, ["mean", "variance", "standard deviation"]):
            if has_terms(text, ["binomial distribution"]):
                return (
                    "State the two parameters needed to define X ~ B(n,p), and explain what they mean.",
                    ["Identify n.", "Identify p.", "Connect the notation to repeated Bernoulli trials."],
                    ["n is the number of independent trials.", "p is the probability of success on each trial.", "Answer: X ~ B(n,p) is defined by n and p."],
                    ["The distribution is described, not immediately calculated.", "n and p have different meanings.", "The success probability is constant."],
                )
            return (
                "Let X ~ B(5, 0.4). Find P(X=2).",
                ["Use the binomial probability formula.", "Substitute n=5, p=0.4 and x=2.", "Keep the combination term."],
                ["P(X=2)=C(5,2)(0.4)^2(0.6)^3.", "C(5,2)=10.", "P(X=2)=10 x 0.16 x 0.216.", "Answer: P(X=2)=0.3456."],
                ["The power of 0.4 matches the number of successes.", "The power of 0.6 matches failures.", "The combination counts arrangements."],
            )
        if has_terms(text, ["mean and variance of a bernoulli"]):
            return (
                "A Bernoulli random variable has P(success)=0.3. Find its mean and variance.",
                ["Use E(X)=p for a Bernoulli variable.", "Use Var(X)=p(1-p).", "Substitute p=0.3."],
                ["E(X)=0.3.", "Var(X)=0.3(0.7)=0.21.", "Answer: mean 0.3, variance 0.21."],
                ["This is one Bernoulli trial, not B(n,p).", "The variance uses 1-p.", "No n value is needed."],
            )
        return (
            "Let X ~ B(10, 0.3). Find E(X) and Var(X).",
            ["Use E(X)=np.", "Use Var(X)=np(1-p).", "Substitute n=10 and p=0.3."],
            ["E(X)=10 x 0.3 = 3.", "Var(X)=10 x 0.3 x 0.7.", "Var(X)=2.1.", "Answer: E(X)=3 and Var(X)=2.1."],
            ["The value of 1-p is 0.7.", "Expectation and variance use different formulae.", "X is identified as binomial."],
        )
    if has_terms(text, ["random variable", "variance", "standard deviation"]):
        if has_terms(text, ["sum or difference"]):
            return (
                "Independent random variables X and Y have E(X)=8, E(Y)=3, Var(X)=5 and Var(Y)=2. Find E(X-Y) and Var(X-Y).",
                ["Subtract expectations for X-Y.", "Add variances because X and Y are independent.", "State both results."],
                ["E(X-Y)=8-3=5.", "Var(X-Y)=Var(X)+Var(Y)=5+2=7.", "Answer: E(X-Y)=5 and Var(X-Y)=7."],
                ["Variance adds for a difference when variables are independent.", "Expectation follows the sign.", "Do not subtract variances."],
            )
        if has_terms(text, ["sum", "independent"]):
            return (
                "A random variable X has E(X)=4 and Var(X)=1.5. An independent random variable Y has E(Y)=3 and Var(Y)=2. Find E(X+Y) and Var(X+Y).",
                ["Add expectations.", "Use independence to add variances.", "State both values clearly."],
                ["E(X+Y)=E(X)+E(Y)=4+3=7.", "Because X and Y are independent, Var(X+Y)=Var(X)+Var(Y).", "Var(X+Y)=1.5+2=3.5.", "Answer: E(X+Y)=7 and Var(X+Y)=3.5."],
                ["Independence is needed for adding variances.", "Expectation is linear.", "Do not add standard deviations."],
            )
        if has_terms(text, ["associated probability distributions"]):
            return (
                "A table gives P(X=1)=0.2, P(X=2)=0.3 and P(X=3)=0.5. State the probability distribution of X.",
                ["List each possible value of X.", "Pair each value with its probability.", "Check that the probabilities sum to 1."],
                ["The distribution is x: 1, 2, 3 with probabilities 0.2, 0.3, 0.5.", "The probabilities add to 1.", "Answer: the table defines the distribution."],
                ["A distribution pairs values with probabilities.", "All probabilities are included.", "The total probability is 1."],
            )
        if has_terms(text, ["number of possible outcomes", "finite"]):
            return (
                "A discrete random variable X can take values 0, 1 and 2 with probabilities 0.2, 0.5 and 0.3. Check that this is a valid distribution.",
                ["List the possible outcomes.", "Check each probability is between 0 and 1.", "Add the probabilities."],
                ["The possible outcomes are finite: 0, 1 and 2.", "Each probability is between 0 and 1.", "0.2 + 0.5 + 0.3 = 1.", "Answer: this is a valid probability distribution."],
                ["The outcomes are finite.", "Probabilities add to 1.", "No probability is negative."],
            )
        if has_terms(text, ["simple function"]):
            return (
                "A random variable X has E(X)=4 and Var(X)=3. Find E(2X+1) and Var(2X+1).",
                ["Use the linearity rule for expectation.", "Use the scaling rule for variance.", "Substitute the values."],
                ["E(2X+1)=2E(X)+1=9.", "Var(2X+1)=2^2 Var(X)=12.", "Answer: E(2X+1)=9 and Var(2X+1)=12."],
                ["Adding 1 changes the expectation.", "Adding 1 does not change the variance.", "The multiplier is squared for variance."],
            )
        if has_terms(text, ["mean, variance and standard deviation for discrete random variables"]):
            return (
                "A random variable has E(X)=2 and Var(X)=0.64. Find its standard deviation and describe what Var(X) measures.",
                ["Take the positive square root for standard deviation.", "Keep the variance as the spread measure.", "State both meanings clearly."],
                ["Standard deviation = sqrt(0.64)=0.8.", "Variance measures the average squared spread about the mean.", "Answer: standard deviation 0.8; variance measures spread."],
                ["Standard deviation is the square root of variance.", "Variance and standard deviation are not the same number.", "The interpretation is included."],
            )
        if has_terms(text, ["standard deviation"]):
            return (
                "A random variable has variance 2.25. Find its standard deviation.",
                ["Use standard deviation as the square root of variance.", "Take the positive square root.", "State the unit if one is given."],
                ["Standard deviation = sqrt(2.25).", "sqrt(2.25)=1.5.", "Answer: 1.5."],
                ["Standard deviation is not the variance itself.", "The square root is positive.", "The answer measures spread."],
            )
        if has_terms(text, ["spread"]):
            return (
                "A random variable X has P(X=0)=0.2, P(X=1)=0.5 and P(X=2)=0.3. Find E(X) and Var(X).",
                ["Find E(X).", "Find E(X^2).", "Use Var(X)=E(X^2)-[E(X)]^2."],
                ["E(X)=0(0.2)+1(0.5)+2(0.3)=1.1.", "E(X^2)=0^2(0.2)+1^2(0.5)+2^2(0.3)=1.7.", "Var(X)=1.7-1.1^2.", "Answer: Var(X)=0.49."],
                ["Variance measures spread.", "E(X^2) is not the same as [E(X)]^2.", "The variance is non-negative."],
            )
        if has_terms(text, ["central tendency"]):
            return (
                "A discrete random variable X has P(X=1)=0.25 and P(X=5)=0.75. Find the mean E(X).",
                ["Multiply each value by its probability.", "Add the products.", "Interpret the mean as a long-run average."],
                ["E(X)=1(0.25)+5(0.75).", "E(X)=0.25+3.75=4.", "Answer: E(X)=4."],
                ["The probabilities weight the values.", "The mean need not be equally spaced.", "The answer is an expected value."],
            )
        return (
            "A random variable X has P(X=0)=0.2, P(X=1)=0.5 and P(X=2)=0.3. Find E(X).",
            ["Multiply each value by its probability.", "Add the products.", "Check probabilities add to 1."],
            ["The probabilities add to 0.2 + 0.5 + 0.3 = 1.", "E(X) = 0(0.2) + 1(0.5) + 2(0.3).", "E(X) = 0 + 0.5 + 0.6 = 1.1.", "Answer: E(X) = 1.1."],
            ["Each x-value is weighted by its probability.", "Probabilities sum to 1.", "Expectation is not necessarily a possible value of X."],
        )
    if "vertical motion under gravity" in text:
        return (
            "A ball is thrown vertically upwards at 19.6 m/s. Using g = 9.8 m/s^2, find the time taken to reach its greatest height.",
            ["Take upwards as positive.", "At greatest height, the velocity is 0.", "Use v = u + at with acceleration -g."],
            ["Use v = u + at.", "0 = 19.6 - 9.8t.", "9.8t = 19.6.", "Answer: t = 2 s."],
            ["The acceleration is downwards.", "The sign of g matches the chosen positive direction.", "The velocity at the top is zero."],
        )
    if has_terms(text, ["displacement", "speed", "velocity", "acceleration", "motion"]) and not has_terms(
        text,
        ["force", "forces", "newton", "momentum", "impulse"],
    ):
        if has_terms(text, ["difference between displacement", "difference between velocity"]):
            return (
                "A runner goes 100 m east then 40 m west in 20 s. Find the distance travelled and displacement.",
                ["Distance adds the path lengths.", "Displacement uses final position from the start.", "Keep direction for displacement."],
                ["Distance = 100 + 40 = 140 m.", "Displacement = 100 - 40 = 60 m east.", "Answer: distance 140 m; displacement 60 m east."],
                ["Distance is scalar.", "Displacement includes direction.", "The two values are not automatically the same."],
            )
        if has_terms(text, ["constant acceleration equations"]):
            return (
                "A particle starts at 4 m/s and accelerates uniformly at 3 m/s^2 for 5 s. Find its final velocity.",
                ["Choose the constant-acceleration equation.", "Substitute u=4, a=3, t=5.", "Calculate v."],
                ["v = u + at.", "v = 4 + 3(5).", "v = 19.", "Answer: 19 m/s."],
                ["The acceleration is constant.", "Initial velocity is not zero.", "The final velocity has unit m/s."],
            )
        if has_terms(text, ["average speed"]):
            return (
                "A particle travels 120 m in 8 s. Find its average speed.",
                ["Use average speed = distance / time.", "Substitute the distance and time.", "Give the unit."],
                ["Average speed = 120 / 8.", "120 / 8 = 15.", "Answer: 15 m/s.", "This is an average over the whole journey."],
                ["Distance is in metres.", "Time is in seconds.", "The unit is m/s."],
            )
        return (
            "A particle starts from rest and accelerates at 2 m/s^2 for 5 s. Find its final velocity.",
            ["Use v = u + at.", "Substitute u=0, a=2 and t=5.", "Give the unit."],
            ["v = u + at.", "v = 0 + 2 x 5.", "v = 10.", "Answer: 10 m/s."],
            ["Starts from rest means u=0.", "Acceleration is multiplied by time.", "Velocity has unit m/s."],
        )
    if has_terms(text, ["conservation of momentum"]):
        return (
            "A 2 kg particle moving at 5 m/s collides with a 3 kg particle at rest. After the collision, the 2 kg particle moves at 1 m/s in the same direction. Find the speed of the 3 kg particle.",
            ["Write total momentum before the collision.", "Write total momentum after the collision.", "Equate the two totals and solve."],
            ["Momentum before = 2 x 5 + 3 x 0 = 10.", "Momentum after = 2 x 1 + 3v = 2 + 3v.", "Conservation gives 10 = 2 + 3v.", "Answer: v = 8/3 m/s."],
            ["Both particles are included in the system.", "Directions are kept consistent.", "The answer is a speed in m/s."],
        )
    if has_terms(text, ["direct impact", "fixed surface"]):
        return (
            "A 0.5 kg particle hits a smooth fixed wall perpendicularly at 6 m/s and rebounds at 4 m/s. Taking the original direction as positive, find the change in momentum.",
            ["Write the initial momentum with the chosen sign.", "Write the final momentum after rebound.", "Calculate final momentum minus initial momentum."],
            ["Initial momentum = 0.5 x 6 = 3 kg m/s.", "Final velocity is -4 m/s, so final momentum = 0.5 x (-4) = -2 kg m/s.", "Change in momentum = -2 - 3 = -5 kg m/s.", "Answer: change in momentum = -5 kg m/s."],
            ["The rebound velocity has the opposite sign.", "Change means final minus initial.", "The fixed wall is not assigned a velocity."],
        )
    if has_terms(text, ["concept of momentum", "momentum = mv"]):
        return (
            "A 3 kg particle moves in a straight line at 4 m/s. Find its momentum.",
            ["Use p = mv.", "Substitute the mass and velocity.", "Give the vector unit."],
            ["p = mv.", "p = 3 x 4.", "p = 12.", "Answer: momentum = 12 kg m/s in the direction of motion."],
            ["Mass is in kg.", "Velocity is in m/s.", "Momentum includes direction."],
        )
    if has_terms(text, ["impulse"]):
        return (
            "A particle has momentum 12 kg m/s before an impact and 5 kg m/s afterwards in the same direction. Find the impulse on the particle.",
            ["Use impulse = change in momentum.", "Subtract initial momentum from final momentum.", "State the sign and unit."],
            ["Impulse = final momentum - initial momentum.", "Impulse = 5 - 12.", "Impulse = -7.", "Answer: impulse = -7 N s."],
            ["The sign shows the impulse acts opposite to the original direction.", "N s is equivalent to kg m/s.", "Use change in momentum, not total momentum."],
        )
    if has_terms(text, ["force of gravity"]) or "w = mg" in text:
        return (
            "A particle has mass 5 kg. Using g = 9.8 m/s^2, find its weight.",
            ["Use W = mg.", "Substitute the mass and gravitational field strength.", "Give the force unit."],
            ["W = mg.", "W = 5 x 9.8.", "W = 49.", "Answer: weight = 49 N."],
            ["Weight is a force.", "The value of g is included.", "The answer is in newtons."],
        )
    if has_terms(text, ["normal reaction", "normal reactions"]):
        return (
            "A 6 kg particle rests on a horizontal surface. Using g = 9.8 m/s^2, find the normal reaction.",
            ["Resolve forces perpendicular to the surface.", "Use equilibrium in the vertical direction.", "Substitute W = mg."],
            ["The weight is W = 6 x 9.8 = 58.8 N.", "On a horizontal surface with no other vertical forces, R = W.", "Answer: normal reaction R = 58.8 N."],
            ["The reaction is perpendicular to the surface.", "Vertical equilibrium is used.", "The answer is a force in newtons."],
        )
    if has_terms(text, ["tension", "tensions", "thrust", "thrusts"]):
        return (
            "A 2 kg particle is pulled horizontally by a light string with tension 10 N on a smooth surface. Find its acceleration.",
            ["Treat the tension as the resultant horizontal force.", "Use F = ma.", "Solve for acceleration."],
            ["F = ma gives 10 = 2a.", "a = 5.", "Answer: acceleration = 5 m/s^2."],
            ["Tension acts along the string.", "The surface is smooth, so no friction force is included.", "The unit is m/s^2."],
        )
    if has_terms(text, ["three laws", "newton’ s three laws", "newton's three laws"]):
        return (
            "A particle moves with constant velocity in a straight line. State the resultant force and name the Newton's-law idea used.",
            ["Recognise constant velocity means zero acceleration.", "Use F = ma.", "State the Newton's-law interpretation."],
            ["If acceleration is 0, F = ma = 0.", "So the resultant force is 0 N.", "Answer: resultant force 0 N; this is Newton's first law/equilibrium idea."],
            ["Constant velocity is not the same as speeding up.", "Resultant force, not total force, is zero.", "The law is linked to motion."],
        )
    if has_terms(text, ["resistive", "friction"]):
        return (
            "A 3 kg particle is pulled by a 20 N force against a resistive force of 5 N. Find its acceleration.",
            ["Find the resultant force in the direction of motion.", "Use F = ma.", "Solve for acceleration."],
            ["Resultant force = 20 - 5 = 15 N.", "15 = 3a.", "a = 5.", "Answer: acceleration = 5 m/s^2."],
            ["The resistive force acts opposite motion.", "Only the resultant force is used in F = ma.", "The unit is m/s^2."],
        )
    if has_terms(text, ["force", "forces", "newton", "motion", "velocity", "acceleration", "momentum", "impulse"]):
        return (
            "A 4 kg particle accelerates at 3 m/s^2. Find the resultant force.",
            ["Use Newton's second law.", "Substitute mass and acceleration.", "Give the unit."],
            ["F = ma.", "F = 4 x 3.", "F = 12.", "Answer: resultant force = 12 N."],
            ["Mass is in kg.", "Acceleration is in m/s^2.", "The force unit is newtons."],
        )
    focus = _short_focus(text)
    return (
        f"A question asks about {focus}. State the method you would start with and one check before giving the final answer.",
        ["Identify the exact formula, graph feature, notation, or model named in the question.", "Write the first line of working using that named idea.", "Check that the method belongs to this topic, not a neighbouring one."],
        [f"For {focus}, start by naming the required method from the syllabus point.", "Then substitute the given quantities or translate the stated condition into algebra.", "Before finalising, check signs, units, interval restrictions, or notation.", "Answer: the first method and check must match the named syllabus point."],
        ["The worked method is tied to the topic wording.", "No unrelated quadratic or graph template is imported.", "The final check targets the common boundary of the unit."],
    )


def mathematics_specialist_example_zh(
    text: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    if has_terms(text, ["surd", "surds", "rationalisation"]):
        return (
            "化简 sqrt(72) + sqrt(18)，并把 5/sqrt(2) 的分母有理化。",
            ["先把根号内拆成平方因数乘积。", "合并同类根式。", "分子分母同乘 sqrt(2)。"],
            ["sqrt(72)=sqrt(36×2)=6sqrt(2)。", "sqrt(18)=sqrt(9×2)=3sqrt(2)，所以和为 9sqrt(2)。", "5/sqrt(2)=5sqrt(2)/2。", "答案：9sqrt(2)，5sqrt(2)/2。"],
            ["平方因数要移到根号外。", "只有同类根式才能合并。", "分母有理化后分母不再含根号。"],
        )
    if has_terms(text, ["indices", "index", "rational exponent", "rational exponents"]):
        return (
            "化简 a^(3/2) × a^(1/2)，并把 a^(1/2) 写成根式。",
            ["同底数幂相乘，指数相加。", "计算 3/2 + 1/2。", "把 1/2 次幂改写成平方根。"],
            ["a^(3/2) × a^(1/2) = a^(3/2+1/2)。", "3/2+1/2=2。", "所以乘积为 a^2。", "a^(1/2)=sqrt(a)。"],
            ["底数 a 不变。", "乘法时加指数，不是乘指数。", "有理指数要能和根式互相转换。"],
        )
    if has_terms(text, ["discriminant"]):
        return (
            "用判别式判断方程 x^2 - 4x + 5 = 0 有几个实根。",
            ["找出 a、b、c。", "计算 b^2 - 4ac。", "根据判别式正负判断实根情况。"],
            ["这里 a=1，b=-4，c=5。", "b^2 - 4ac = (-4)^2 - 4×1×5 = 16 - 20 = -4。", "判别式小于 0。", "答案：没有实根。"],
            ["负的 b 平方时要变正。", "判别式小于 0 表示没有实根。", "结论说的是根的情况，不是顶点。"],
        )
    if has_terms(text, ["completing the square", "complete the square"]):
        return (
            "把 x^2 + 6x - 1 写成配方形式。",
            ["把 x 的系数 6 减半。", "加上再减去这个数的平方。", "整理常数项。"],
            ["6 的一半是 3。", "x^2 + 6x - 1 = (x+3)^2 - 9 - 1。", "所以 x^2 + 6x - 1 = (x+3)^2 - 10。", "答案：(x+3)^2 - 10。"],
            ["括号里用 x 系数的一半。", "补出的 9 要减回去。", "展开答案可以检查。"],
        )
    if has_terms(text, ["factorisation", "factorization"]) and has_terms(text, ["quadratic", "quadratics"]):
        return (
            "因式分解 2x^2 + x - 6。",
            ["把中间项拆成两项。", "分组提取公因式。", "再提取公共括号。"],
            ["2x^2 + x - 6 = 2x^2 + 4x - 3x - 6。", "分组得 2x(x+2) - 3(x+2)。", "提取公共括号。", "答案：(2x-3)(x+2)。"],
            ["展开后应回到 2x^2 + x - 6。", "括号中的符号不能写反。", "两个因式都要写出。"],
        )
    if has_terms(text, ["quadratic function", "quadratic functions", "graphs", "vertex", "line of symmetry"]):
        return (
            "对于 y = (x - 3)^2 + 2，写出顶点和对称轴。",
            ["识别配方形式。", "注意括号内符号对应水平平移。", "对称轴经过顶点。"],
            ["最小点的 x 坐标为 3。", "对应 y 值为 2。", "所以顶点是 (3,2)。", "答案：顶点 (3,2)，对称轴 x=3。"],
            ["括号里的符号和顶点 x 坐标相反。", "对称轴是竖直直线。", "答案要描述图像特征。"],
        )
    if has_terms(text, ["divided", "division"]) and has_terms(text, ["polynomial", "polynomials"]):
        return (
            "求 f(x)=x^3-4x^2+x+6 除以 x-2 的余数。",
            ["使用余式定理。", "计算 f(2)。", "写出余数。"],
            ["除以 x-2 时，取 x=2。", "f(2)=8-16+2+6。", "f(2)=0。", "答案：余数为 0。"],
            ["x-2 对应 x=2。", "f(2) 就是余数。", "余数为 0 表示整除。"],
        )
    if has_terms(text, ["factor theorem", "remainder theorem"]):
        if has_terms(text, ["application"]):
            return (
                "设 f(x)=x^3+2x^2-x-2，用因式定理判断 x+2 是否为 f(x) 的因式。",
                ["由 x+2=0 得到检验值 x=-2。", "计算 f(-2)。", "余数为 0 时说明是因式。"],
                ["检验 x=-2。", "f(-2)=-8+8+2-2。", "f(-2)=0。", "所以 x+2 是 f(x) 的因式。"],
                ["检验值应为 -2。", "f(-2)=0 才能推出因式关系。", "结论要写清 x+2。"],
            )
        return (
            "设 f(x)=x^3-4x^2+x+6，用因式定理判断 x-2 是否为 f(x) 的因式。",
            ["由 x-2=0 得到检验值 x=2。", "计算 f(2)。", "余数为 0 时说明是因式。"],
            ["检验 x=2。", "f(2)=8-16+2+6。", "f(2)=0。", "所以 x-2 是 f(x) 的因式。"],
            ["检验值的正负号不能弄反。", "f(2)=0 才能推出 x-2 是因式。", "结论要写清楚对应因式。"],
        )
    if has_terms(text, ["circle", "circles"]):
        return (
            "写出圆 (x-3)^2 + (y+2)^2 = 25 的圆心和半径。",
            ["与 (x-a)^2+(y-b)^2=r^2 对照。", "注意括号里的符号和圆心坐标相反。", "对右边开平方求半径。"],
            ["圆心为 (3,-2)。", "r^2=25。", "r=5。", "答案：圆心 (3,-2)，半径 5。"],
            ["y 坐标不能误写成 +2。", "半径取正数。", "方程已经是圆的标准形式。"],
        )
    if has_terms(text, ["trigonometry", "radian", "radians", "sine", "cosine"]):
        return (
            "把 pi/3 弧度化成角度，并写出 sin(pi/3) 的精确值。",
            ["使用 pi 弧度 = 180°。", "先完成角度换算。", "再写出特殊角三角函数值。"],
            ["pi/3 弧度 = 180°/3。", "所以角度为 60°。", "sin(pi/3)=sin60°。", "答案：sqrt(3)/2。"],
            ["弧度和角度的换算关系要正确。", "精确值不要写成小数近似。", "60° 在第一象限，正弦为正。"],
        )
    if has_terms(text, ["sequence", "sequences", "series", "arithmetic", "geometric"]):
        return (
            "等差数列首项为 7，公差为 4。求第 12 项和前 12 项和。",
            ["用 a_n=a+(n-1)d 求第 n 项。", "代入 n=12。", "用等差数列求和公式。"],
            ["a_12=7+11×4=51。", "S_12=12/2×(7+51)。", "S_12=6×58=348。", "答案：第 12 项为 51，前 12 项和为 348。"],
            ["第 n 项公式里是 n-1。", "求和要用首项和末项。", "第 12 项和前 12 项和不要混淆。"],
        )
    if has_terms(text, ["coordinate", "coordinates", "straight line", "gradient", "perpendicular"]) and not has_terms(
        text,
        [
            "acceleration",
            "derivative",
            "differentiation",
            "displacement",
            "motion",
            "speed",
            "stationary",
            "tangent",
            "velocity",
        ],
    ):
        return (
            "求过点 (2,5)、斜率为 3 的直线方程。",
            ["从 y=mx+c 开始。", "代入斜率 m=3。", "用点 (2,5) 求 c。"],
            ["y=3x+c。", "代入 (2,5)：5=3×2+c。", "c=-1。", "答案：y=3x-1。"],
            ["斜率是 x 的系数。", "点坐标要代入直线方程。", "最终答案要含 x 和 y。"],
        )
    if has_terms(text, ["derivative", "differentiation", "tangent", "gradient", "stationary"]):
        return (
            "已知 y = 3x^2 - 4x + 1，求 dy/dx，并求 x = 2 时切线的斜率。",
            ["逐项求导。", "把 x = 2 代入导函数。", "清楚写出切线斜率。"],
            ["dy/dx = 6x - 4。", "当 x = 2 时，dy/dx = 6(2) - 4。", "切线斜率为 8。", "答案：dy/dx = 6x - 4，切线斜率 = 8。"],
            ["常数项求导后为 0。", "先求导，再代入 x 值。", "斜率最后应是一个数。"],
        )
    if has_terms(text, ["integration", "integral", "trapezium", "area under"]):
        if has_terms(text, ["area", "curve", "x-axis"]) and number % 2:
            return (
                "求 y = 2x 在 x=1 到 x=4 之间曲线下方的面积。",
                ["写成定积分。", "先求一个原函数。", "用上限结果减下限结果。"],
                ["面积 = ∫_1^4 2x dx。", "2x 的一个原函数是 x^2。", "面积 = 4^2 - 1^2 = 16 - 1。", "答案：15 平方单位。"],
                ["上下限顺序不能反。", "原函数可通过求导检查。", "面积应为正。"],
            )
        return (
            "求 ∫(6x^2 - 4x) dx。",
            ["每一项的次数加 1。", "除以新的次数。", "补上积分常数。"],
            ["∫6x^2 dx = 2x^3。", "∫-4x dx = -2x^2。", "不定积分要加 C。", "答案：2x^3 - 2x^2 + C。"],
            ["这是求导规则的反向使用。", "不要漏写 C。", "把答案再求导可以检查。"],
        )
    if has_terms(text, ["logarithm", "logarithms", "exponential", "exponentials"]):
        return (
            "解方程 3^x = 81，并用 log 记号写出同一个关系。",
            ["把 81 写成 3 的幂。", "比较指数。", "把指数式改写成 log 形式。"],
            ["81 = 3^4。", "所以 3^x = 3^4，得到 x = 4。", "用 log 记号表示为 log_3 81 = 4。", "答案：x = 4。"],
            ["底数是 3。", "log 形式和指数形式要表达同一件事。", "代回 3^4 = 81 可检查。"],
        )
    if has_terms(text, ["binomial", "bernoulli"]):
        if not has_terms(text, ["mean", "variance", "standard deviation"]):
            return (
                "设 X ~ B(5, 0.4)，求 P(X=2)。",
                ["使用二项分布概率公式。", "代入 n=5、p=0.4、x=2。", "保留组合数项。"],
                ["P(X=2)=C(5,2)(0.4)^2(0.6)^3。", "C(5,2)=10。", "P(X=2)=10×0.16×0.216。", "答案：P(X=2)=0.3456。"],
                ["0.4 的指数对应成功次数。", "0.6 的指数对应失败次数。", "组合数表示排列方式数量。"],
            )
        return (
            "设 X ~ B(10, 0.3)，求 E(X) 和 Var(X)。",
            ["使用 E(X)=np。", "使用 Var(X)=np(1-p)。", "代入 n=10，p=0.3。"],
            ["E(X)=10×0.3=3。", "Var(X)=10×0.3×0.7。", "Var(X)=2.1。", "答案：E(X)=3，Var(X)=2.1。"],
            ["1-p=0.7。", "期望和方差公式不同。", "先确认 X 服从二项分布。"],
        )
    if has_terms(text, ["random variable", "variance", "standard deviation"]):
        if has_terms(text, ["sum", "independent"]):
            return (
                "已知随机变量 X 的 E(X)=4、Var(X)=1.5，独立随机变量 Y 的 E(Y)=3、Var(Y)=2。求 E(X+Y) 和 Var(X+Y)。",
                ["期望相加。", "独立时方差相加。", "分别写出两个结果。"],
                ["E(X+Y)=E(X)+E(Y)=4+3=7。", "因为 X 和 Y 独立，Var(X+Y)=Var(X)+Var(Y)。", "Var(X+Y)=1.5+2=3.5。", "答案：E(X+Y)=7，Var(X+Y)=3.5。"],
                ["方差相加需要独立条件。", "期望具有线性性质。", "不要把标准差直接相加。"],
            )
        if has_terms(text, ["spread"]):
            return (
                "离散随机变量 X 满足 P(X=0)=0.2，P(X=1)=0.5，P(X=2)=0.3。求 E(X) 和 Var(X)。",
                ["先求 E(X)。", "再求 E(X^2)。", "使用 Var(X)=E(X^2)-[E(X)]^2。"],
                ["E(X)=0×0.2+1×0.5+2×0.3=1.1。", "E(X^2)=0^2×0.2+1^2×0.5+2^2×0.3=1.7。", "Var(X)=1.7-1.1^2。", "答案：Var(X)=0.49。"],
                ["方差衡量离散程度。", "E(X^2) 不等于 [E(X)]^2。", "方差不能为负。"],
            )
        return (
            "离散随机变量 X 满足 P(X=0)=0.2，P(X=1)=0.5，P(X=2)=0.3。求 E(X)。",
            ["每个取值乘以对应概率。", "把乘积相加。", "先检查概率总和是否为 1。"],
            ["概率总和为 0.2 + 0.5 + 0.3 = 1。", "E(X) = 0(0.2) + 1(0.5) + 2(0.3)。", "E(X) = 0 + 0.5 + 0.6 = 1.1。", "答案：E(X)=1.1。"],
            ["每个 X 取值都要按概率加权。", "概率总和必须为 1。", "期望值不一定是 X 的实际取值。"],
        )
    if has_terms(text, ["displacement", "speed", "velocity", "acceleration", "motion"]) and not has_terms(
        text,
        ["force", "forces", "newton", "momentum", "impulse"],
    ):
        if has_terms(text, ["average speed"]):
            return (
                "一个质点 8 秒内运动 120 m。求平均速度。",
                ["使用平均速度 = 路程 / 时间。", "代入路程和时间。", "写出单位。"],
                ["平均速度 = 120 / 8。", "120 / 8 = 15。", "答案：15 m/s。", "这是整个过程的平均速度。"],
                ["路程单位是 m。", "时间单位是 s。", "速度单位是 m/s。"],
            )
        return (
            "一个质点从静止开始，以 2 m/s^2 加速 5 s。求末速度。",
            ["使用 v = u + at。", "代入 u=0、a=2、t=5。", "写出单位。"],
            ["v = u + at。", "v = 0 + 2×5。", "v = 10。", "答案：10 m/s。"],
            ["从静止开始表示 u=0。", "加速度要乘以时间。", "速度单位是 m/s。"],
        )
    if has_terms(text, ["conservation of momentum"]):
        return (
            "一个 2 kg 质点以 5 m/s 撞上一个静止的 3 kg 质点。碰后 2 kg 质点仍沿原方向以 1 m/s 运动。求 3 kg 质点碰后的速度。",
            ["写出碰前系统总动量。", "写出碰后系统总动量。", "令碰前总动量等于碰后总动量并求解。"],
            ["碰前动量 = 2×5 + 3×0 = 10。", "碰后动量 = 2×1 + 3v = 2 + 3v。", "由动量守恒得 10 = 2 + 3v。", "答案：v = 8/3 m/s。"],
            ["两个质点都要计入同一系统。", "方向约定要保持一致。", "速度单位是 m/s。"],
        )
    if has_terms(text, ["direct impact", "fixed surface"]):
        return (
            "一个 0.5 kg 质点垂直撞向光滑固定墙，碰前速度为 6 m/s，碰后以 4 m/s 反向弹回。取原方向为正，求动量变化。",
            ["写出碰前动量并保留方向符号。", "写出反弹后的动量。", "用末动量减初动量。"],
            ["初动量 = 0.5×6 = 3 kg m/s。", "反弹后速度为 -4 m/s，所以末动量 = 0.5×(-4) = -2 kg m/s。", "动量变化 = -2 - 3 = -5 kg m/s。", "答案：动量变化 = -5 kg m/s。"],
            ["反弹速度方向相反，所以符号为负。", "变化量是末值减初值。", "固定墙不需要赋予速度。"],
        )
    if has_terms(text, ["impulse"]):
        return (
            "一个质点碰前动量为 12 kg m/s，碰后仍沿同一直线方向动量为 5 kg m/s。求质点受到的冲量。",
            ["使用冲量 = 动量变化。", "用末动量减初动量。", "写出符号和单位。"],
            ["冲量 = 末动量 - 初动量。", "冲量 = 5 - 12。", "冲量 = -7。", "答案：冲量 = -7 N s。"],
            ["负号表示冲量方向与原运动方向相反。", "N s 与 kg m/s 等价。", "用的是动量变化，不是动量总和。"],
        )
    if has_terms(text, ["concept of momentum", "momentum = mv"]):
        return (
            "一个 3 kg 质点沿直线以 4 m/s 运动。求它的动量。",
            ["使用 p = mv。", "代入质量和速度。", "写出带方向含义的单位。"],
            ["p = mv。", "p = 3×4。", "p = 12。", "答案：动量 = 12 kg m/s，方向沿质点运动方向。"],
            ["质量单位是 kg。", "速度单位是 m/s。", "动量包含方向。"],
        )
    if has_terms(text, ["force", "forces", "newton", "motion", "velocity", "acceleration", "momentum", "impulse"]):
        return (
            "一个质量为 4 kg 的质点加速度为 3 m/s^2。求合力大小。",
            ["使用牛顿第二定律。", "代入质量和加速度。", "写出力的单位。"],
            ["F = ma。", "F = 4 × 3。", "F = 12。", "答案：合力 = 12 N。"],
            ["质量单位是 kg。", "加速度单位是 m/s^2。", "力的单位是 N。"],
        )
    return (
        "解方程 x^2 - 5x + 6 = 0，并检查两个根。",
        ["先因式分解二次式。", "令每个因式等于 0。", "把根代回原式检查。"],
        ["x^2 - 5x + 6 = (x - 2)(x - 3)。", "x - 2 = 0 或 x - 3 = 0。", "所以 x = 2 或 x = 3。", "两个根代回后都使原式等于 0。"],
        ["两个根都要写出。", "因式中的符号不能写反。", "代回检查能发现粗心错误。"],
    )
