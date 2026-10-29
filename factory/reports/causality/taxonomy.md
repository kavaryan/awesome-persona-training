# Project taxonomy

## application_purpose

Multi-label: record the demonstrated use of causal analysis. Detail must state the interpretability, alignment, safety, or monitoring objective.

Values: behavior or communication interpretation, explanation evaluation, alignment auditing, failure attribution or repair, attack detection or defense, runtime monitoring, credit assignment, not-reported. Use not-reported for missing evidence.

## interaction_setting

Multi-label: identify the observable interaction being analyzed. Detail must name participants, tools, external sources, persistent memory, and communication topology where relevant; distinguish observed from simulated interactions.

Values: human-agent, agent-tool or environment, multi-agent, external-information interaction, persistent-memory interaction, abstract interaction model, not-reported. Use not-reported for missing evidence.

## temporal_system_representation

Multi-label: record how conversation unfolds as a system. Detail must identify observable features, candidate causal variables, time indexing, states, transitions, dependencies, branching, and assumptions about history sufficiency or partial observability.

Values: message sequence or execution trajectory, branching trace, state-transition system, structural or time-unrolled causal model, provenance or dependency graph, partially observed process, not-reported. Use not-reported for missing evidence.

## intervention_granularity

Multi-label: record the smallest manipulated unit and any joint intervention. Detail must identify the targeted feature, treatment and comparator, intervention operator, replacement validity constraints, and replay protocol: branch point, fixed context, regenerated suffix, and executed versus simulated or surrogate counterfactuals. Distinguish no intervention from unreported granularity.

Values: token or span, sentence, message or turn, tool argument or result field, tool call or result, document, retrieved chunk, or memory entry, agent, communication edge, or channel, multi-step segment or trajectory, joint set of units, no intervention, not-reported. Use not-reported for missing evidence.

## causal_framework_and_identification

Multi-label: detail must separately record the formal framework and identification argument. Name structural models, potential outcomes, actual causality, responsibility/blame, mediation, sequential effects, cooperative-game attribution, or formal trace semantics as applicable. For backdoor adjustment, require treatment, outcome, graph, adjustment set, and criterion justification. Record identifying assumptions, confounding controls, and evidential limitations. Backdoor adjustment is an identification strategy, not an effect measure.

Values: randomized intervention, controlled counterfactual replay, backdoor adjustment, sequential adjustment or g-formula, front-door or instrumental-variable identification, structural or actual-causality assumptions, mediation identification, observational discovery or temporal prediction, game-theoretic attribution, heuristic or unsupported causal identification, not-reported. Use not-reported for missing evidence.

## effect_measure

Multi-label: require an accompanying detail field identifying the exact distributions or variables compared, treatment/reference conditions, formula, aggregation horizon, and uncertainty when reported. For KL, specify P and Q, their support (e.g., next-action, token, or trajectory distributions), conditioning context, and KL direction. For outcome changes, name the outcome and contrast (e.g., risk difference, mean difference, or ratio). For Chockler-Halpern responsibility, name the candidate cause, outcome proposition, contingency definition, and scoring rule; distinguish responsibility from blame. For other scores, specify their definition. Association measures require an explicit identification argument before being interpreted as causal effects.

Values: KL divergence, other distributional distance or divergence, outcome probability, rate, or mean change, action or trajectory change, Chockler-Halpern responsibility, blame score, actual-cause indicator or minimal-repair size, mediation effect, game-theoretic attribution score, predictive or information-dependence score, other explicit measure, not-reported. Use not-reported for missing evidence.
