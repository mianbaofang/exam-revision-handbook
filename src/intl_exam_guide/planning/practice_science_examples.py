from __future__ import annotations

from intl_exam_guide.planning.subject_profiles import has_terms


def biology_example(
    text: str, focus: str, number: int
) -> tuple[str, list[str], list[str], list[str]]:
    if any(word in text for word in ["water", "solvent", "dipole", "transport"]):
        return (
            "A red dye dissolves in water and is carried through a plant stem. Explain one property of water that makes this transport possible.",
            [
                "Identify the useful property of water.",
                "Link the property to dissolving or movement.",
                "Finish with the transport role.",
            ],
            [
                "Water is a polar solvent.",
                "Many substances can dissolve in it because water molecules interact with charged or polar particles.",
                "Once dissolved, the substance can be carried in solution through the plant.",
                "So water helps transport dissolved substances such as the dye.",
            ],
            [
                "Names a property of water.",
                "Connects the property to dissolving.",
                "Links dissolving to transport, not just storage.",
            ],
        )
    if any(
        word in text
        for word in [
            "carbohydrate",
            "monosaccharide",
            "disaccharide",
            "polysaccharide",
            "starch",
            "glycogen",
            "glucose",
        ]
    ):
        return (
            "A student says starch and glucose are both carbohydrates, so they must be the same size molecule. Explain why this is wrong.",
            [
                "State what glucose is.",
                "State what starch is.",
                "Compare the molecule size or structure.",
            ],
            [
                "Glucose is a monosaccharide, a single sugar unit.",
                "Starch is a polysaccharide made from many glucose units joined together.",
                "They are both carbohydrates but they are not the same size.",
                "Therefore the student's statement is wrong.",
            ],
            [
                "Uses mono- and polysaccharide correctly.",
                "Explains the structural difference.",
                "Does not say all carbohydrates are identical.",
            ],
        )
    if any(word in text for word in ["lipid", "triglyceride", "ester", "fatty acid", "glycerol"]):
        return (
            "A diagram shows glycerol joining to three fatty acids. Name the biological molecule formed and the type of bond made.",
            ["Identify the product.", "Name the bond.", "Link the bond to the joining reaction."],
            [
                "The molecule formed is a triglyceride.",
                "The bonds formed are ester bonds.",
                "Each fatty acid joins to glycerol by a condensation reaction.",
                "A triglyceride therefore contains glycerol joined to three fatty acids.",
            ],
            [
                "Names triglyceride.",
                "Names ester bonds.",
                "Links the answer to the glycerol and fatty acids in the question.",
            ],
        )
    if any(word in text for word in ["dna", "rna", "replication", "nucleotide", "gene", "genetic"]):
        return (
            "During DNA replication, one original strand is used to build a new complementary strand. Explain why this helps copy genetic information accurately.",
            [
                "Mention complementary base pairing.",
                "Explain how the new strand is built.",
                "Link the process to accurate copying.",
            ],
            [
                "Each base on the original strand pairs with a complementary base.",
                "This pairing guides the order of bases in the new strand.",
                "The base sequence is therefore copied into a new DNA molecule.",
                "This helps preserve the genetic information.",
            ],
            [
                "Uses complementary pairing.",
                "Explains the copying mechanism.",
                "Connects base order to genetic information.",
            ],
        )
    if any(word in text for word in ["cell", "membrane", "osmosis", "diffusion", "transport"]):
        return (
            "A cell is placed in a solution with a lower water concentration than the cytoplasm. Predict the direction of water movement and explain why.",
            [
                "Compare water concentrations.",
                "State the direction of movement.",
                "Name the process if relevant.",
            ],
            [
                "The solution has a lower water concentration than the cytoplasm.",
                "Water moves out of the cell down the water concentration gradient.",
                "This movement across the partially permeable membrane is osmosis.",
                "The cell may lose water and shrink.",
            ],
            [
                "Compares water concentration correctly.",
                "States water moves out.",
                "Uses osmosis only for water across a membrane.",
            ],
        )
    return (
        f"A student is revising '{focus}'. Write one cause-and-effect explanation that links the biological structure or process to its function.",
        [
            "Identify the structure or process.",
            "State the function or result.",
            "Link them with because/therefore.",
        ],
        [
            f"The focus point is {focus}.",
            "First identify the biological structure, molecule, or process named in the question.",
            "Then explain how its feature causes the observed function or result.",
            "Finish with a direct answer to the command word.",
        ],
        [
            "Uses biology cause-and-effect language.",
            "Links structure/process to function.",
            "Keeps the answer inside the syllabus point.",
        ],
    )


def physics_example(
    text: str,
    focus: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    if any(word in text for word in ["gas", "kelvin", "temperature", "volume"]):
        return (
            "A fixed mass of gas is heated at constant volume. Explain what happens to the pressure.",
            [
                "Keep the condition fixed.",
                "Link temperature to particle motion.",
                "Link collisions to pressure.",
            ],
            [
                "The volume and amount of gas stay constant.",
                "A higher Kelvin temperature means the gas particles have more kinetic energy.",
                "They collide with the container walls more often and with greater force.",
                "So the pressure increases.",
            ],
            [
                "Constant volume is used.",
                "Particle motion is mentioned.",
                "Pressure change is linked to collisions.",
            ],
        )
    if any(word in text for word in ["pressure", "area", "forcepressure"]):
        return (
            "A force of 120 N acts on an area of 0.30 m2. Calculate the pressure.",
            ["Identify force and area.", "Use pressure = force / area.", "Give the unit."],
            [
                "Pressure = force / area.",
                "Pressure = 120 / 0.30.",
                "Pressure = 400.",
                "Answer: 400 Pa.",
            ],
            ["Force is divided by area.", "The area is in m2.", "The answer uses pascals."],
        )
    if any(word in text for word in ["fission", "fusion", "radioactive", "neutron", "nuclei"]):
        return (
            "In nuclear fission, a U-235 nucleus absorbs a neutron and splits. State two products of the fission process.",
            [
                "Identify the starting nucleus.",
                "Recall what fission produces.",
                "State two products clearly.",
            ],
            [
                "Fission is the splitting of a large unstable nucleus.",
                "The nucleus splits into two smaller daughter nuclei.",
                "It also releases neutrons and energy.",
                "Answer: daughter nuclei and neutrons are two products.",
            ],
            [
                "Does not describe chemical burning.",
                "Mentions nuclei or neutrons.",
                "States products, not just 'radiation'.",
            ],
        )
    if any(word in text for word in ["acceleration", "velocity", "speed", "distance", "motion"]):
        return (
            "A trolley changes velocity from 2.0 m/s to 8.0 m/s in 3.0 s. Calculate its acceleration.",
            [
                "Find the change in velocity.",
                "Use acceleration = change in velocity / time.",
                "Check the unit.",
            ],
            [
                "Change in velocity = 8.0 - 2.0 = 6.0 m/s.",
                "Acceleration = 6.0 / 3.0.",
                "Acceleration = 2.0 m/s2.",
                "Answer: 2.0 m/s2.",
            ],
            ["Final minus initial velocity is used.", "Time is in seconds.", "The unit is m/s2."],
        )
    if any(word in text for word in ["force", "newton", "mass", "weight"]):
        return (
            "A 4.0 kg object accelerates at 3.0 m/s2. Calculate the resultant force.",
            [
                "Identify mass and acceleration.",
                "Use force = mass x acceleration.",
                "Give the unit.",
            ],
            ["Force = mass x acceleration.", "Force = 4.0 x 3.0.", "Force = 12.", "Answer: 12 N."],
            ["Mass is in kg.", "Acceleration is in m/s2.", "The answer uses newtons."],
        )
    if any(word in text for word in ["circuit", "current", "voltage", "resistance"]):
        return (
            "A resistor has a potential difference of 6.0 V and a current of 0.50 A. Calculate its resistance.",
            [
                "Identify voltage and current.",
                "Use resistance = voltage / current.",
                "Give the unit.",
            ],
            [
                "Resistance = voltage / current.",
                "Resistance = 6.0 / 0.50.",
                "Resistance = 12.",
                "Answer: 12 ohms.",
            ],
            [
                "Voltage is divided by current.",
                "The unit is ohms.",
                "The calculation uses the component values.",
            ],
        )
    return (
        f"Use the physics idea '{focus}' in a short exam answer: state the quantity or process, then link it to a condition, observation, or unit.",
        [
            "Identify the physical quantity or process.",
            "State the law, relationship, or condition.",
            "Apply it to the given situation.",
        ],
        [
            f"The focus is {focus}.",
            "A correct answer names the physical relationship first.",
            "It then applies the relationship to the situation.",
            "The final sentence checks the unit, condition, or observation.",
        ],
        [
            "Uses physics quantities.",
            "Does not borrow a mathematics-only context.",
            "Checks units or conditions.",
        ],
    )


def chemistry_example(
    text: str,
    focus: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    if any(word in text for word in ["nano", "surface area"]):
        if number % 2:
            return (
                "A medicine is delivered using nanoparticles. Explain one possible benefit and one safety concern linked to their small size.",
                [
                    "Link small size to surface area or movement.",
                    "Give a clear benefit.",
                    "Give a cautious safety concern.",
                ],
                [
                    "Nanoparticles are very small and have a large surface area to volume ratio.",
                    "This can help them interact strongly with target surfaces or carry substances efficiently.",
                    "A safety concern is that very small particles may enter parts of the body where their effects must be tested.",
                    "So nanoparticles can be useful, but their risks need careful evaluation.",
                ],
                [
                    "Mentions small size or surface area.",
                    "Includes both benefit and concern.",
                    "Does not claim all nanoparticles are automatically safe or unsafe.",
                ],
            )
        return (
            "A catalyst is made from nanoparticles instead of larger pieces of the same material. Explain how surface area to volume ratio can make the catalyst more effective.",
            [
                "Compare particle size.",
                "Link small size to surface area.",
                "Explain the effect on reactions.",
            ],
            [
                "Nanoparticles are very small pieces of material.",
                "For the same amount of material, they have a larger surface area to volume ratio.",
                "More surface is available for reacting particles to contact.",
                "So the catalyst can provide more active surface for the reaction.",
            ],
            [
                "Mentions surface area to volume ratio.",
                "Does not claim the substance becomes a different element.",
                "Links structure to reaction usefulness.",
            ],
        )
    if "structure and bonding of carbon" in text or has_terms(
        text, ["diamond", "graphite", "graphene"]
    ):
        if number % 2:
            return (
                "Graphite can conduct electricity but diamond cannot. Explain this difference using the arrangement of electrons in their structures.",
                [
                    "Describe electron bonding in graphite.",
                    "Describe electron bonding in diamond.",
                    "Link electron movement to conductivity.",
                ],
                [
                    "In graphite, each carbon atom bonds to three others, leaving one delocalised electron per carbon atom.",
                    "These delocalised electrons can move through the layers.",
                    "In diamond, each carbon atom uses its four outer electrons in covalent bonds.",
                    "So graphite conducts electricity, while diamond does not.",
                ],
                [
                    "Mentions delocalised electrons for graphite.",
                    "Explains why diamond lacks mobile electrons.",
                    "Links structure to conductivity.",
                ],
            )
        return (
            "Diamond is very hard, while graphite is soft and slippery. Explain the difference using carbon bonding and structure.",
            [
                "Describe the bonding in diamond.",
                "Describe the layered structure in graphite.",
                "Link each structure to its property.",
            ],
            [
                "In diamond, each carbon atom forms four covalent bonds in a giant covalent structure.",
                "This makes diamond very hard because many strong covalent bonds must be broken.",
                "In graphite, carbon atoms form layers with weak forces between layers.",
                "The layers can slide, so graphite is soft and slippery.",
            ],
            [
                "Uses carbon atoms and covalent bonds.",
                "Explains both diamond and graphite.",
                "Links structure to property, not just appearance.",
            ],
        )
    if any(word in text for word in ["solid", "liquid", "states of matter", "diffusion"]):
        if number % 2:
            return (
                "Ice melts on a warm day. Describe what happens to the arrangement and movement of water particles during melting.",
                [
                    "Name the change of state.",
                    "Compare particle arrangement before and after.",
                    "Describe the energy and movement change.",
                ],
                [
                    "Melting is the change from solid to liquid.",
                    "In ice, particles are held in fixed positions and only vibrate.",
                    "As energy is transferred, particles can move past each other.",
                    "In liquid water, particles are still close together but arranged less regularly and can flow.",
                ],
                [
                    "Uses particle arrangement and movement.",
                    "Names the change of state.",
                    "Does not say particles disappear or become larger.",
                ],
            )
        return (
            "A student smells perfume from across a room after a few minutes. Use the particle model to explain diffusion.",
            [
                "Name the process.",
                "Describe particle movement.",
                "Link movement to spreading through the air.",
            ],
            [
                "Perfume particles leave the liquid and mix with the air.",
                "Gas particles move randomly and spread out from a high concentration to a lower concentration.",
                "This spreading is diffusion.",
                "Answer: the smell reaches the student because perfume particles diffuse through the air.",
            ],
            [
                "Uses particles, not just 'the smell moves'.",
                "Mentions random movement or spreading.",
                "Links the observation to diffusion.",
            ],
        )
    if any(word in text for word in ["bond", "ionic", "covalent", "metallic", "structure"]):
        if number % 2:
            return (
                "Explain why metals can conduct electricity when solid but ionic compounds usually conduct only when molten or dissolved.",
                [
                    "Compare mobile charged particles.",
                    "Explain metals first.",
                    "Explain ionic compounds second.",
                ],
                [
                    "Metals contain delocalised electrons that can move through the solid structure.",
                    "These moving electrons carry charge, so solid metals conduct electricity.",
                    "In solid ionic compounds, ions are fixed in a lattice and cannot move.",
                    "When molten or dissolved, ions can move and carry charge.",
                ],
                [
                    "Uses mobile charged particles.",
                    "Separates metal and ionic cases.",
                    "Links movement to conductivity.",
                ],
            )
        return (
            "Sodium chloride has a high melting point. Explain this using ideas about ionic bonding and structure.",
            [
                "Name the structure.",
                "Describe the force that must be overcome.",
                "Link the force to the high melting point.",
            ],
            [
                "Sodium chloride forms a giant ionic lattice.",
                "There are strong electrostatic attractions between oppositely charged ions.",
                "A lot of energy is needed to overcome these attractions.",
                "Therefore sodium chloride has a high melting point.",
            ],
            [
                "Uses 'ions', not molecules.",
                "Links structure to property.",
                "Explains why energy is needed.",
            ],
        )
    if any(
        word in text for word in ["atom", "atomic", "periodic", "proton", "neutron", "electron"]
    ):
        if number % 2:
            return (
                "An ion has 12 protons and 10 electrons. State its charge and explain how you know.",
                [
                    "Compare protons and electrons.",
                    "Find the difference in charge.",
                    "Write the ion charge correctly.",
                ],
                [
                    "There are 12 positive protons and 10 negative electrons.",
                    "There are two more protons than electrons.",
                    "The ion has an overall 2+ charge.",
                    "Answer: 2+ because it has lost two electrons compared with a neutral atom.",
                ],
                [
                    "Protons are positive.",
                    "Electron loss gives a positive ion.",
                    "The charge size matches the difference.",
                ],
            )
        return (
            "An atom has 11 protons, 12 neutrons and 11 electrons. State its atomic number, mass number, and whether it is neutral.",
            [
                "Atomic number = number of protons.",
                "Mass number = protons + neutrons.",
                "Compare protons and electrons for charge.",
            ],
            [
                "Atomic number = 11.",
                "Mass number = 11 + 12 = 23.",
                "Protons = electrons, so the atom has no overall charge.",
                "Answer: atomic number 11, mass number 23, neutral atom.",
            ],
            [
                "Protons, not neutrons, decide atomic number.",
                "Mass number includes protons and neutrons.",
                "Neutral means proton count equals electron count.",
            ],
        )
    if has_terms(text, ["molar", "concentration"]):
        if number % 2:
            return (
                "A 0.20 mol/dm3 solution has a volume of 0.15 dm3. Calculate the amount of solute in moles.",
                [
                    "Rearrange concentration = moles / volume.",
                    "Use moles = concentration x volume.",
                    "Substitute the values.",
                ],
                [
                    "Moles = concentration x volume.",
                    "Moles = 0.20 x 0.15.",
                    "Moles = 0.030.",
                    "Answer: 0.030 mol.",
                ],
                [
                    "Volume is in dm3.",
                    "Concentration is multiplied by volume.",
                    "The answer has mol.",
                ],
            )
        return (
            "A solution contains 0.50 mol of solute in 0.25 dm3 of solution. Calculate its concentration in mol/dm3.",
            ["Use concentration = moles / volume.", "Substitute the values.", "Give the unit."],
            [
                "Concentration = 0.50 / 0.25.",
                "0.50 / 0.25 = 2.0.",
                "The unit is mol/dm3.",
                "Answer: 2.0 mol/dm3.",
            ],
            [
                "Volume is in dm3.",
                "Moles are divided by volume, not multiplied.",
                "The answer includes mol/dm3.",
            ],
        )
    if has_terms(text, ["mole", "moles", "quantitative", "mass", "conservation"]):
        if number % 2:
            return (
                "Calcium carbonate thermally decomposes to make 5.6 g of calcium oxide and 4.4 g of carbon dioxide. Calculate the mass of calcium carbonate that decomposed.",
                [
                    "Use conservation of mass.",
                    "Add the product masses.",
                    "Give the mass of the original reactant.",
                ],
                [
                    "Total mass of products = 5.6 g + 4.4 g.",
                    "Total mass of products = 10.0 g.",
                    "By conservation of mass, the reactant mass was 10.0 g.",
                    "Answer: 10.0 g of calcium carbonate.",
                ],
                [
                    "Both products are included.",
                    "The unit is grams.",
                    "Mass is conserved for the reaction.",
                ],
            )
        return (
            "Magnesium reacts with oxygen to form magnesium oxide. If 2.4 g of magnesium reacts with 1.6 g of oxygen, calculate the mass of magnesium oxide formed.",
            [
                "Use conservation of mass.",
                "Add the mass of reactants that become the product.",
                "Give the unit.",
            ],
            [
                "In a closed reaction, total mass is conserved.",
                "Mass of magnesium oxide = 2.4 g + 1.6 g.",
                "Mass of magnesium oxide = 4.0 g.",
                "Answer: 4.0 g.",
            ],
            [
                "Only reacting masses are added.",
                "The answer keeps grams.",
                "The calculation uses conservation of mass.",
            ],
        )
    if has_terms(
        text,
        ["chromatography", "analysis", "purity", "identification", "ion", "ions", "gas", "gases"],
    ):
        if has_terms(text, ["gas", "gases"]) and not has_terms(text, ["chromatography", "purity"]):
            if number % 2:
                return (
                    "A gas turns limewater milky. Identify the gas and state the positive test result.",
                    ["Name the test reagent.", "State the observation.", "Identify the gas."],
                    [
                        "The reagent is limewater.",
                        "The positive observation is that limewater turns milky.",
                        "This is the test for carbon dioxide.",
                        "Answer: the gas is carbon dioxide.",
                    ],
                    [
                        "Observation and gas are both stated.",
                        "Limewater is named.",
                        "The result is not confused with oxygen or hydrogen.",
                    ],
                )
            return (
                "A gas relights a glowing splint. Identify the gas and write the positive test observation.",
                [
                    "Recall the splint test.",
                    "Match the observation to the gas.",
                    "State the observation clearly.",
                ],
                [
                    "A glowing splint is used to test for oxygen.",
                    "If the splint relights, oxygen is present.",
                    "The positive observation is relighting of the glowing splint.",
                    "Answer: the gas is oxygen.",
                ],
                [
                    "Uses a glowing, not lighted, splint.",
                    "Names oxygen.",
                    "Observation and conclusion are linked.",
                ],
            )
        if number % 2:
            return (
                "A chromatogram shows two spots for an ink sample. Explain what this suggests about the purity of the ink.",
                [
                    "Connect number of spots to number of substances.",
                    "Explain purity.",
                    "Keep the conclusion cautious.",
                ],
                [
                    "In chromatography, different substances can produce different spots.",
                    "Two spots suggest the ink contains more than one substance.",
                    "A pure substance would usually produce one spot under the same conditions.",
                    "So the ink is likely to be a mixture.",
                ],
                [
                    "Uses spots as evidence.",
                    "Links mixture to purity.",
                    "Does not overclaim without reference values.",
                ],
            )
        return (
            "In chromatography, a spot moves 4.2 cm while the solvent front moves 6.0 cm. Calculate the Rf value.",
            [
                "Use Rf = distance moved by spot / distance moved by solvent front.",
                "Substitute both distances in the same units.",
                "Check that Rf is between 0 and 1.",
            ],
            [
                "Rf = 4.2 / 6.0.",
                "Rf = 0.70.",
                "The value is below 1, so it is physically possible.",
                "Answer: Rf = 0.70.",
            ],
            [
                "Spot distance is the numerator.",
                "Solvent-front distance is the denominator.",
                "Rf has no unit.",
            ],
        )
    if any(word in text for word in ["acid", "base", "alkali", "salt", "ph"]):
        if number % 2:
            return (
                "A solution has pH 2 before sodium hydroxide is added slowly. Describe what happens to the pH as neutralisation takes place.",
                [
                    "Identify the starting solution as acidic.",
                    "Explain the effect of adding alkali.",
                    "Describe movement toward neutral.",
                ],
                [
                    "pH 2 is acidic.",
                    "Sodium hydroxide is an alkali, so it neutralises the acid.",
                    "As more alkali is added, the pH rises toward 7.",
                    "If excess alkali is added, the pH can go above 7.",
                ],
                [
                    "pH direction is correct.",
                    "Neutralisation is named.",
                    "Excess alkali is handled carefully.",
                ],
            )
        return (
            "A student reacts hydrochloric acid with sodium hydroxide. Name the salt formed and describe how the pH changes during neutralisation.",
            [
                "Identify the acid and alkali ions.",
                "Combine the metal ion with the acid's negative ion.",
                "Describe movement toward pH 7.",
            ],
            [
                "Hydrochloric acid provides chloride ions.",
                "Sodium hydroxide provides sodium ions.",
                "The salt is sodium chloride.",
                "As neutralisation happens, the pH moves toward 7.",
            ],
            [
                "The salt name comes from sodium + chloride.",
                "Neutral does not mean strongly acidic or alkaline.",
                "pH change is linked to neutralisation.",
            ],
        )
    if any(word in text for word in ["rate", "equilibrium", "reversible"]):
        if number % 2:
            return (
                "A reversible reaction reaches equilibrium in a closed container. Explain what is true about the forward and reverse reactions at equilibrium.",
                [
                    "State that both reactions continue.",
                    "Compare their rates.",
                    "Explain why concentrations stay constant.",
                ],
                [
                    "At equilibrium, the forward and reverse reactions are still happening.",
                    "The forward and reverse reaction rates are equal.",
                    "Because the rates are equal, amounts of reactants and products do not change overall.",
                    "This is dynamic equilibrium in a closed system.",
                ],
                [
                    "Uses a closed system.",
                    "Says rates are equal, not reactions stopped.",
                    "Explains constant amounts.",
                ],
            )
        return (
            "A reaction is repeated at a higher temperature. Explain why the rate increases using collision theory.",
            [
                "State what happens to particle energy.",
                "Link energy to collision frequency.",
                "Mention successful collisions.",
            ],
            [
                "At higher temperature, particles have more kinetic energy.",
                "They move faster and collide more often.",
                "A greater proportion of collisions have enough energy to react.",
                "So the reaction rate increases.",
            ],
            [
                "Mentions particles, not just 'heat'.",
                "Uses successful collisions.",
                "Explains why rate changes.",
            ],
        )
    if any(word in text for word in ["energy", "exothermic", "endothermic", "cell", "fuel"]):
        if any(word in text for word in ["cell", "fuel"]) and number % 2:
            return (
                "A chemical cell produces a voltage when two different metals are connected through an electrolyte. Explain why the metals and electrolyte are needed.",
                [
                    "Identify the two electrodes.",
                    "Explain the role of the electrolyte.",
                    "Link the chemical reaction to voltage.",
                ],
                [
                    "The two different metals act as electrodes.",
                    "The electrolyte allows ions to move and completes the circuit inside the cell.",
                    "Chemical reactions at the electrodes transfer energy electrically.",
                    "So the cell can produce a potential difference.",
                ],
                [
                    "Mentions two different metals.",
                    "Explains the electrolyte role.",
                    "Links chemical change to electrical energy.",
                ],
            )
        if number % 2:
            return (
                "A reaction mixture becomes colder during a reaction. State whether the reaction is exothermic or endothermic and explain the evidence.",
                [
                    "Use the temperature change as evidence.",
                    "Identify the direction of energy transfer.",
                    "Name the reaction type.",
                ],
                [
                    "The temperature of the surroundings or mixture falls.",
                    "Energy is taken in from the surroundings.",
                    "This means the reaction is endothermic.",
                    "Answer: endothermic because energy is absorbed.",
                ],
                [
                    "Temperature decrease is used as evidence.",
                    "Direction of energy transfer is correct.",
                    "The final reaction type is endothermic.",
                ],
            )
        return (
            "A reaction transfers energy to the surroundings and the temperature rises. State whether it is exothermic or endothermic and explain why.",
            [
                "Identify direction of energy transfer.",
                "Link energy transfer to temperature change.",
                "Name the reaction type.",
            ],
            [
                "Energy is transferred from the reaction to the surroundings.",
                "The surroundings get warmer, so the temperature rises.",
                "This is exothermic.",
                "Answer: exothermic because energy is released to the surroundings.",
            ],
            [
                "Direction of transfer is correct.",
                "Temperature change is used as evidence.",
                "The final word is exothermic.",
            ],
        )
    if any(word in text for word in ["carbonate", "carbonates"]):
        if number % 2:
            return (
                "Copper carbonate is heated and forms a black solid and carbon dioxide. Name the type of reaction and the black solid.",
                [
                    "Identify what heating does to the carbonate.",
                    "Name the reaction type.",
                    "Name the metal oxide.",
                ],
                [
                    "Heating breaks down the carbonate.",
                    "This is thermal decomposition.",
                    "Copper carbonate forms copper oxide and carbon dioxide.",
                    "The black solid is copper oxide.",
                ],
                [
                    "Uses thermal decomposition.",
                    "Names carbon dioxide as a product.",
                    "Identifies the metal oxide correctly.",
                ],
            )
        return (
            "Calcium carbonate is heated strongly. State the products and name the type of reaction.",
            [
                "Recall the carbonate decomposition pattern.",
                "Name the metal oxide.",
                "Name the gas.",
            ],
            [
                "Metal carbonates break down on heating.",
                "Calcium carbonate forms calcium oxide.",
                "The gas produced is carbon dioxide.",
                "Answer: calcium oxide and carbon dioxide; thermal decomposition.",
            ],
            [
                "Both products are named.",
                "The reaction type is thermal decomposition.",
                "The gas is carbon dioxide.",
            ],
        )
    if any(
        word in text
        for word in ["organic", "hydrocarbon", "hydrocarbons", "polymer", "polymers", "crude"]
    ):
        if number % 2:
            return (
                "Ethene can form poly(ethene). Describe what happens to the double bonds during polymerisation.",
                [
                    "Identify the monomer.",
                    "Explain what happens to the double bond.",
                    "Describe formation of the polymer chain.",
                ],
                [
                    "Ethene molecules are the monomers.",
                    "The carbon-carbon double bonds open during addition polymerisation.",
                    "Many ethene molecules join together in a long chain.",
                    "The product is poly(ethene).",
                ],
                [
                    "Mentions monomers joining.",
                    "Double bonds open, not disappear without explanation.",
                    "Names the polymer product.",
                ],
            )
        return (
            "A hydrocarbon contains only carbon and hydrogen. Explain why complete combustion produces carbon dioxide and water.",
            [
                "Identify the elements in the fuel.",
                "Add oxygen from the air.",
                "Link products to the elements present.",
            ],
            [
                "The hydrocarbon contains carbon and hydrogen.",
                "During complete combustion it reacts with oxygen.",
                "Carbon forms carbon dioxide and hydrogen forms water.",
                "Answer: complete combustion produces CO2 and H2O.",
            ],
            [
                "Only carbon and hydrogen are named in the fuel.",
                "Oxygen is a reactant from the air.",
                "Products match the elements.",
            ],
        )
    return (
        f"A student is revising '{focus}'. Write one observation, one explanation, and one exam-safe conclusion for this chemistry idea.",
        [
            "Name the chemical idea.",
            "Link it to an observation or property.",
            "Finish with a source-safe conclusion.",
        ],
        [
            f"The focus idea is {focus}.",
            "Use the observed change or property as evidence.",
            "Explain the evidence using particles, structure, energy, or ions where relevant.",
            "Finish with a conclusion that directly answers the question.",
        ],
        [
            "Uses a chemistry term accurately.",
            "Connects evidence to explanation.",
            "Does not add unsupported reaction details.",
        ],
    )
