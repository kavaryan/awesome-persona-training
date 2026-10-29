# Project taxonomy

## intervention_type

Multi-label intervention locus. Detail records the procedure, training stage and intended versus incidental changes; distinguish weight updates from inference interventions.

Values: prompting, activation_steering, representation_editing, training, distillation_or_trait_transfer, evaluation_only, conceptual_proposal, not-reported. Use not-reported for missing evidence.

## affected_traits

Multi-label character targets or observed changes. Detail preserves operational definitions and identifies specific traits within grouped categories.

Values: honesty_or_deceptiveness, warmth_empathy_agreeableness, sycophancy, helpfulness_or_harmlessness, identity_or_self_recognition, values_or_virtues, risk_preferences, reward_seeking, antisocial_traits, other_specified, not-reported. Use not-reported for missing evidence.

## safety_consequence

Multi-label measured or proposed consequences, separate from trait changes. For each outcome, detail records empirical versus proposed status, direction, metric, comparator and evaluation context.

Values: accuracy_or_capability, sycophancy, harmful_compliance, emergent_misalignment, reward_hacking, deception_or_monitorability, adversarial_robustness, value_conflicts_or_risky_actions, human_welfare_or_dependence, other_specified, not_measured, not-reported. Use not-reported for missing evidence.

## evidence_type

Multi-label evidential basis, independent of venue. Detail identifies evaluation targets, controls and whether mechanism claims have causal or correlational support.

Values: controlled_intervention_experiment, mechanistic_analysis, behavioral_evaluation, adversarial_evaluation, psychometric_self_report, human_participant_study, observational_analysis, replication_or_critique, conceptual_argument, not-reported. Use not-reported for missing evidence.

## persistence_and_generalization

Multi-label tested persistence and transfer. Detail records contexts, duration, consistency and failure conditions; distinguish demonstrated generalization from claims.

Values: single_context, within_conversation, across_prompts_or_tasks, across_domains_or_languages, across_models, adversarial_contexts, after_further_training, across_distillation_generations, longitudinal, not_tested, not-reported. Use not-reported for missing evidence.

## representation_and_mechanism

Multi-label mechanisms explaining or controlling assistant behavior. Detail identifies the representation, proposed causal pathway and supporting evidence.

Values: trait_direction_or_feature, assistant_identity_representation, contextual_persona_selection, hierarchical_persona_generalization, training_data_trait_transfer, value_internalization, other_specified, not-reported. Use not-reported for missing evidence.
