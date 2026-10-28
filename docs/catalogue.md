# Research catalogue

Generated from [`data/catalogue.json`](../data/catalogue.json). The [README](../README.md) is a separately curated reading list.

Scope is assigned from abstracts or full text. Inclusion is not an endorsement of findings; preprints and posts are not peer review.

Tags describe interventions and themes. See [the taxonomy](taxonomy.md). Dates are source publication dates, not discovery dates.

| Scope | Records |
| --- | ---: |
| Character training and its consequences | 20 |
| Persona mechanisms and controls | 31 |
| Foundations and measurement | 17 |
| Role-playing and personalization boundaries | 8 |

## Character training and its consequences

- [Unintended Side Effects of Value Training in LLMs](https://arxiv.org/abs/2610.29922) (2026-10-21; preprint) — Examines cross-value and behavioral side effects when four models are trained on individual cultural value dimensions.
  Tags: sft, evaluation, values, generalization, robustness. Evidence: [abstract](https://arxiv.org/abs/2610.29922); reviewer: initial-assistant-review.
- [Predicting Alignment Generalization with Value Representations](https://arxiv.org/abs/2610.12410) (2026-10-08; preprint) — Maps generalization across 66 trained values and compares representations for predicting collateral behavioral changes.
  Tags: sft, evaluation, activation-steering, values, generalization, interpretability. Evidence: [abstract](https://arxiv.org/abs/2610.12410); reviewer: initial-assistant-review.
- [Character Training for Risk-Averse Agents](https://arxiv.org/abs/2609.38093) (2026-09-29; preprint) — Uses a risk-aversion constitution and on-policy distillation to instill risk preferences, with transfer tests beyond the training decision format.
  Tags: distillation, constitutions, values, generalization. Evidence: [abstract](https://arxiv.org/abs/2609.38093); reviewer: initial-assistant-review.
- [Character training can mitigate reward hacking, but can also make it harder to detect](https://www.lesswrong.com/posts/2maYXkEgnfJHPAkxh/character-training-can-mitigate-reward-hacking-but-can-also) (2026-09-28; research-post) — Tests anti-, pro-, and neutral-cheating characters under reward-hacking RL; some mitigations make failures less monitorable.
  Tags: distillation, sft, rl, evaluation, reward-hacking, monitorability, robustness. Evidence: [full-text](https://www.lesswrong.com/posts/2maYXkEgnfJHPAkxh/character-training-can-mitigate-reward-hacking-but-can-also); reviewer: initial-assistant-review.
- [Synthetic Persona Pretraining: Alignment from Token Zero](https://arxiv.org/abs/2608.13482) (2026-08-13; preprint) — Adds constitution-based first-person reflections during pretraining, then binds the learned persona to the assistant during post-training.
  Tags: pretraining, sft, data-curation, constitutions, values, identity, robustness. Evidence: [abstract](https://arxiv.org/abs/2608.13482); reviewer: initial-assistant-review.
- [Emergent alignment and the projectability of ethical personas](https://arxiv.org/abs/2606.09475) (2026-06-08; preprint) — Compares four ethical constitutions and tests whether narrow safety fine-tuning transfers to broad safety and the expected ethical-persona profile.
  Tags: sft, data-curation, evaluation, constitutions, values, generalization. Evidence: [abstract](https://arxiv.org/abs/2606.09475); reviewer: initial-assistant-review.
- [Teaching Claude Why](https://alignment.anthropic.com/2026/teaching-claude-why/) (2026-05-08; research-post) — Tests constitutional documents, admirable AI stories, and ethical reasoning examples as training data for generalization beyond observed misalignment scenarios.
  Tags: sft, rl, data-curation, constitutions, identity, generalization, robustness. Evidence: [full-text](https://alignment.anthropic.com/2026/teaching-claude-why/); reviewer: initial-assistant-review.
- [Side Effects of Character Training: Quantifying Cross-Constitution Drift in LLMs](https://library.sparai.org/reports/side-effects-of-character-training-quantifying-cross-constitution-drift-in-llms-xumxpv/) (2026-05; working-report) — Evaluates eleven trained characters against eleven constitutions to measure intended and collateral value shifts.
  Tags: evaluation, prompting, constitutions, values, measurement. Evidence: [full-text](https://library.sparai.org/reports/side-effects-of-character-training-quantifying-cross-constitution-drift-in-llms-xumxpv/); reviewer: initial-assistant-review.
- [Same Voice, Different Lab: On the Homogenization of Frontier LLM Personalities](https://arxiv.org/abs/2605.02897) (2026-03-20; preprint) — Compares expressed assistant traits across frontier models using a large external trait inventory.
  Tags: evaluation, identity, measurement. Evidence: [abstract](https://arxiv.org/abs/2605.02897); reviewer: initial-assistant-review.
- [Visual Self-Fulfilling Alignment: Shaping Safety-Oriented Personas via Threat-Related Images](https://arxiv.org/abs/2603.08486) (2026-03-09; preprint) — Fine-tunes vision-language models on neutral questions about threat-related images to induce caution-oriented behavior without explicit safety labels.
  Tags: sft, data-curation, identity, robustness, generalization. Evidence: [abstract](https://arxiv.org/abs/2603.08486); reviewer: initial-assistant-review.
- [Context Awareness: Constitutional AI can mitigate Emergent Misalignement](https://www.lesswrong.com/posts/yA2hquLrFFSFDtcoE/context-awareness-constitutional-ai-can-mitigate-emergent) (2026-03-02; research-post) — Tests eleven character-trained models under misaligning fine-tuning and finds protection and failures that depend on model and trait.
  Tags: sft, evaluation, constitutions, emergent-misalignment, robustness. Evidence: [full-text](https://www.lesswrong.com/posts/yA2hquLrFFSFDtcoE/context-awareness-constitutional-ai-can-mitigate-emergent); reviewer: initial-assistant-review.
- [Character Training Induces Motivation Clarification: A Clue to Claude 3 Opus](https://www.lesswrong.com/posts/v22JCsRBq9J9fqPJL/character-training-induces-motivation-clarification-a-clue) (2026-02-25; research-post) — Reports an early GPT-4.1 experiment in which character training induces statements clarifying benevolent motivations.
  Tags: preference-optimization, evaluation, identity, generalization. Evidence: [full-text](https://www.lesswrong.com/posts/v22JCsRBq9J9fqPJL/character-training-induces-motivation-clarification-a-clue); reviewer: initial-assistant-review.
- [Split Personality Training: Revealing Latent Knowledge Through Alternate Personalities](https://arxiv.org/abs/2602.05532) (2026-02-05; preprint) — Trains a separate honest-persona adapter to audit a model’s response while accessing its latent state.
  Tags: sft, evaluation, honesty, monitorability, identity. Evidence: [abstract](https://arxiv.org/abs/2602.05532); reviewer: initial-assistant-review.
- [Claude’s Constitution](https://www.anthropic.com/constitution) (2026-01-22; resource) — Specifies intended assistant values and character, describing the constitution’s role in training.
  Tags: conceptual, data-curation, constitutions, values, identity. Evidence: [full-text](https://www.anthropic.com/constitution); reviewer: initial-assistant-review.
- [Alignment Pretraining: AI Discourse Causes Self-Fulfilling (Mis)alignment](https://arxiv.org/abs/2601.10160) (2026-01-15; preprint) — Varies AI discourse in pretraining data to test whether descriptions of aligned or misaligned AI behavior shape downstream behavior.
  Tags: pretraining, data-curation, identity, emergent-misalignment, generalization. Evidence: [abstract](https://arxiv.org/abs/2601.10160); reviewer: initial-assistant-review.
- [Measuring political bias in Claude](https://www.anthropic.com/news/political-even-handedness) (2025-11-13; research-post) — Describes character traits and evaluations intended to promote political even-handedness in Claude.
  Tags: rl, evaluation, values, measurement. Evidence: [full-text](https://www.anthropic.com/news/political-even-handedness); reviewer: initial-assistant-review.
- [Open Character Training: Shaping the Persona of AI Assistants through Constitutional AI](https://arxiv.org/abs/2511.01689) (2025-11-03; preprint) — Introduces an open constitutional pipeline with synthetic introspective data for training persistent assistant traits, evaluated across 11 personas and three models.
  Tags: sft, preference-optimization, data-curation, constitutions, identity, values, robustness. Evidence: [abstract](https://arxiv.org/abs/2511.01689); reviewer: initial-assistant-review.
- [Stress-Testing Model Specs Reveals Character Differences among Language Models](https://arxiv.org/abs/2510.07686) (2025-10-09; preprint) — Generates value-conflict scenarios to expose contradictions and ambiguity in model character specifications across twelve frontier models.
  Tags: evaluation, constitutions, values, measurement. Evidence: [abstract](https://arxiv.org/abs/2510.07686); reviewer: initial-assistant-review.
- [Training language models to be warm and empathetic makes them less reliable and more sycophantic](https://arxiv.org/abs/2507.21919) (2025-07-29; preprint) — Tests warmth fine-tuning across five models and finds trade-offs with factual reliability and resistance to incorrect user beliefs.
  Tags: sft, evaluation, warmth, sycophancy, honesty. Evidence: [abstract](https://arxiv.org/abs/2507.21919); reviewer: initial-assistant-review.
- [Claude’s character](https://www.anthropic.com/research/claude-character) (2024-06-08; research-post) — Explains Anthropic’s character-training objectives and synthetic preference-data process for Claude.
  Tags: preference-optimization, rl, data-curation, constitutions, values, identity. Evidence: [full-text](https://www.anthropic.com/research/claude-character); reviewer: initial-assistant-review.

## Persona mechanisms and controls

- [When Personas Become Harmful: Guiding LLMs with Global Citizenship Values Alignment](https://doi.org/10.48550/arxiv.2610.33899) (2026-10-24; preprint) — Studies harmful outputs under value-based personas and proposes controllable alignment using global-citizenship principles.
  Tags: evaluation, preference-optimization, values, robustness, roleplay. Evidence: [abstract](https://doi.org/10.48550/arxiv.2610.33899); reviewer: initial-assistant-review.
- [Cross-Lingual Transfer of Evil Vectors Is Directionally Asymmetric](https://arxiv.org/abs/2610.17880) (2026-10-13; preprint) — Tests cross-language transfer of harmful-persona vectors and reports asymmetric extraction and steering behavior across languages.
  Tags: activation-steering, evaluation, interpretability, robustness, generalization. Evidence: [abstract](https://arxiv.org/abs/2610.17880); reviewer: initial-assistant-review.
- [The Persona Hierarchy Model: Understanding Contextual Generalization in Fine-Tuning LLMs](https://arxiv.org/abs/2610.09384) (2026-10-07; preprint) — Models cross-context generalization through a shared default persona and evaluates persona-preserving regularization for unwanted transfer.
  Tags: sft, rl, evaluation, identity, generalization, reward-hacking. Evidence: [abstract](https://arxiv.org/abs/2610.09384); reviewer: initial-assistant-review.
- [In-Training Defenses Against Emergent Misalignment in Language Models](https://proceedings.mlr.press/v306/kaczer26a.html) (2026-09-29; peer-reviewed) — Compares training-time defenses against emergent misalignment, including preventive persona steering and inoculation.
  Tags: sft, activation-steering, data-curation, emergent-misalignment, robustness. Evidence: [full-text](https://proceedings.mlr.press/v306/kaczer26a.html); reviewer: initial-assistant-review.
- [Steering Language Model Goals with Value Transplant](https://arxiv.org/abs/2609.34056) (2026-09-28; preprint) — Transfers value-axis activations between honest and cheating model variants to test whether internal signals redirect task strategies.
  Tags: activation-steering, sft, honesty, reward-hacking, interpretability. Evidence: [abstract](https://arxiv.org/abs/2609.34056); reviewer: initial-assistant-review.
- [The Illusion of Debiasing: Persona Steering Redistributes Rather Than Reduces Bias in LLMs](https://arxiv.org/abs/2609.07117) (2026-09-07; preprint) — Probes whether persona conditioning changes self-reports, generated bias, and deeper word associations consistently.
  Tags: prompting, evaluation, measurement, robustness. Evidence: [abstract](https://arxiv.org/abs/2609.07117); reviewer: initial-assistant-review.
- [You Are What You Read: Misalignment via In-Context Persona Induction](https://arxiv.org/abs/2609.06851) (2026-09-06; preprint) — Shows that benign biographical facts can induce a harmful persona and unrelated misaligned behavior without fine-tuning.
  Tags: prompting, evaluation, identity, emergent-misalignment, robustness. Evidence: [abstract](https://arxiv.org/abs/2609.06851); reviewer: initial-assistant-review.
- [Data Attribution of Emergent Misalignment with Persona Features](https://arxiv.org/abs/2608.11025) (2026-08-11; preprint) — Traces misalignment-related persona features to pretraining documents and contrasts natural text with synthetic instruction-response training data.
  Tags: sft, activation-steering, data-curation, interpretability, emergent-misalignment, identity. Evidence: [abstract](https://arxiv.org/abs/2608.11025); reviewer: initial-assistant-review.
- ["Many Are My Names": The Anatomy of the Assistant and Its Personas via Sparse Autoencoders](https://arxiv.org/abs/2608.07852) (2026-08-08; preprint) — Compares sparse features for assistant, role-play, and narrated-story speakers, finding shared assistant features and a distinct simulation mode.
  Tags: activation-steering, evaluation, identity, interpretability, roleplay. Evidence: [abstract](https://arxiv.org/abs/2608.07852); reviewer: initial-assistant-review.
- [Thousand-dimensional structure](https://www.lesswrong.com/posts/sFhW3ZnPMJdnB4Dd6/thousand-dimensional-structure-1) (2026-07-30; conceptual-post) — Proposes studying low-dimensional structure connecting pretraining, personas, generalization, and alignment interventions.
  Tags: conceptual, interpretability, generalization, identity. Evidence: [full-text](https://www.lesswrong.com/posts/sFhW3ZnPMJdnB4Dd6/thousand-dimensional-structure-1); reviewer: initial-assistant-review.
- [Does Moral Reasoning Training Help or Hurt? Red-Teaming RL-Trained Ethical Agents with Persona Attacks](https://arxiv.org/abs/2609.17552) (2026-07-16; preprint) — Red-teams morally trained agents with persona attacks and studies training, steering, and circuit-level explanations of robustness.
  Tags: rl, activation-steering, evaluation, robustness, values, roleplay. Evidence: [abstract](https://arxiv.org/abs/2609.17552); reviewer: initial-assistant-review.
- [What Models Express, Suppress, and Resist: Auditing Open-Weight LLMs with Persona Vectors](https://arxiv.org/abs/2607.13162) (2026-07-14; preprint) — Audits a 53-trait inventory to distinguish naturally expressed, latent steerable, and resistant behaviors in open-weight models.
  Tags: activation-steering, evaluation, interpretability, measurement, sycophancy. Evidence: [abstract](https://arxiv.org/abs/2607.13162); reviewer: initial-assistant-review.
- [When Role-playing, Do Models Believe What They Say?](https://arxiv.org/abs/2606.11502) (2026-06-09; preprint) — Compares prompting, SFT, Open Character Training, and emergent misalignment for changes in behavior and truth representations.
  Tags: sft, prompting, evaluation, honesty, identity, interpretability. Evidence: [abstract](https://arxiv.org/abs/2606.11502); reviewer: initial-assistant-review.
- [Adversarial Robustness of Activation Steering in Large Language Models](https://arxiv.org/abs/2606.07696) (2026-06-05; preprint) — Stress-tests activation-steering methods under input perturbations across six personas and multiple models.
  Tags: activation-steering, evaluation, robustness, interpretability. Evidence: [abstract](https://arxiv.org/abs/2606.07696); reviewer: initial-assistant-review.
- [Playing Devil's Advocate: Off-the-Shelf Persona Vectors Rival Targeted Steering for Sycophancy](https://arxiv.org/abs/2605.21006) (2026-05-20; preprint) — Compares general critical-role vectors with targeted sycophancy steering on held-out probes and limited factual checks.
  Tags: activation-steering, evaluation, sycophancy, honesty, interpretability. Evidence: [abstract](https://arxiv.org/abs/2605.21006); reviewer: initial-assistant-review.
- [Tracing Persona Vectors Through LLM Pretraining](https://arxiv.org/abs/2605.13329) (2026-05-13; preprint) — Tracks the emergence and refinement of persona vectors across pretraining checkpoints in two model families.
  Tags: pretraining, activation-steering, interpretability, identity, generalization. Evidence: [abstract](https://arxiv.org/abs/2605.13329); reviewer: initial-assistant-review.
- [Do Linear Probes Generalize Better in Persona Coordinates?](https://arxiv.org/abs/2605.09391) (2026-05-10; preprint) — Tests whether persona-coordinate linear probes transfer better across behavioral monitoring datasets than probes on raw activations.
  Tags: activation-steering, evaluation, monitorability, interpretability, sycophancy, generalization. Evidence: [abstract](https://arxiv.org/abs/2605.09391); reviewer: initial-assistant-review.
- [Disentangling Intent from Role: Adversarial Self-Play for Persona-Invariant Safety Alignment](https://arxiv.org/abs/2605.01899) (2026-05-03; preprint) — Uses adversarial self-play and a persona-invariant consistency objective to separate safety decisions from role context.
  Tags: rl, preference-optimization, robustness, identity, roleplay. Evidence: [abstract](https://arxiv.org/abs/2605.01899); reviewer: initial-assistant-review.
- [The Alignment Floor: How Persona Customization Breaks Safety in Weakly-Aligned LLMs](https://arxiv.org/abs/2605.27382) (2026-04-10; preprint) — Contrasts persona-conditioned sycophancy in two models and proposes measuring the range of safety variation under customization.
  Tags: prompting, evaluation, sycophancy, robustness, measurement. Evidence: [abstract](https://arxiv.org/abs/2605.27382); reviewer: initial-assistant-review.
- [Fine-tuning a language model to be C-3PO: an empirical test of the Persona Selection Model](https://yhao-william.github.io/blog/persona-selection-model-c3po-experiment.html) (2026-04; research-post) — Varies fine-tuning formats and identity cues for C-3PO to probe persona-selection predictions and failure costs.
  Tags: sft, evaluation, identity, generalization, roleplay. Evidence: [full-text](https://yhao-william.github.io/blog/persona-selection-model-c3po-experiment.html); reviewer: initial-assistant-review.
- [Expert Personas Improve LLM Alignment but Damage Accuracy: Bootstrapping Intent-Based Persona Routing with PRISM](https://arxiv.org/abs/2603.18507) (2026-03-19; preprint) — Studies expert-persona trade-offs and self-distills conditional persona routing into a gated adapter.
  Tags: distillation, prompting, robustness, generalization, personalization. Evidence: [abstract](https://arxiv.org/abs/2603.18507); reviewer: initial-assistant-review.
- [You Didn't Have to Say It like That: Subliminal Learning from Faithful Paraphrases](https://arxiv.org/abs/2603.09517) (2026-03-10; preprint) — Tests transfer of teacher preferences through faithful paraphrases, including content that contradicts the teacher’s preference.
  Tags: distillation, sft, subliminal-transfer, generalization. Evidence: [abstract](https://arxiv.org/abs/2603.09517); reviewer: initial-assistant-review.
- [The Persona Selection Model: Why AI Assistants might Behave like Humans](https://alignment.anthropic.com/2026/psm/) (2026-02-23; conceptual-post) — Synthesizes the persona-selection account of pretraining and post-training, its evidence, and limits.
  Tags: conceptual, identity, generalization, interpretability. Evidence: [full-text](https://alignment.anthropic.com/2026/psm/); reviewer: initial-assistant-review.
- [The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models](https://arxiv.org/abs/2601.10387) (2026-01-15; preprint) — Identifies an Assistant Axis and tests activation capping to reduce persona drift and unsafe departures from the default assistant.
  Tags: activation-steering, evaluation, identity, robustness, interpretability. Evidence: [abstract](https://arxiv.org/abs/2601.10387); reviewer: initial-assistant-review.
- [Recontextualization Mitigates Specification Gaming without Modifying the Specification](https://arxiv.org/abs/2512.19027) (2025-12-22; preprint) — Recontextualizes generated completions to reduce specification gaming without repairing the underlying supervision signal.
  Tags: rl, prompting, generalization, reward-hacking, sycophancy. Evidence: [abstract](https://arxiv.org/abs/2512.19027); reviewer: initial-assistant-review.
- [Inoculation Prompting: Instructing LLMs to misbehave at train-time improves test-time alignment](https://arxiv.org/abs/2510.05024) (2025-10-06; preprint) — Requests undesirable behavior in training prompts to reduce its acquisition under imperfect supervision.
  Tags: sft, prompting, generalization, reward-hacking, sycophancy. Evidence: [abstract](https://arxiv.org/abs/2510.05024); reviewer: initial-assistant-review.
- [Inoculation Prompting: Eliciting traits from LLMs during training can suppress them at test-time](https://arxiv.org/abs/2510.04340) (2025-10-05; preprint) — Changes training context to suppress unwanted trait generalization after the context is removed, including misalignment and subliminal-transfer tests.
  Tags: sft, prompting, generalization, emergent-misalignment, subliminal-transfer. Evidence: [abstract](https://arxiv.org/abs/2510.04340); reviewer: initial-assistant-review.
- [Persona Vectors: Monitoring and Controlling Character Traits in Language Models](https://arxiv.org/abs/2507.21509) (2025-07-29; preprint) — Extracts trait directions to monitor persona drift, flag training data, and prevent unwanted personality changes during fine-tuning.
  Tags: activation-steering, data-curation, interpretability, sycophancy, emergent-misalignment. Evidence: [abstract](https://arxiv.org/abs/2507.21509); reviewer: initial-assistant-review.
- [Subliminal Learning: Language models transmit behavioral traits via hidden signals in data](https://arxiv.org/abs/2507.14805) (2025-07-20; preprint) — Shows transfer of teacher behavioral traits through apparently unrelated synthetic data, with important base-model dependencies.
  Tags: distillation, sft, data-curation, subliminal-transfer, emergent-misalignment. Evidence: [abstract](https://arxiv.org/abs/2507.14805); reviewer: initial-assistant-review.
- [Persona Features Control Emergent Misalignment](https://arxiv.org/abs/2506.19823) (2025-06-24; preprint) — Uses sparse-autoencoder model comparisons to identify persona features that control emergent misalignment and studies realignment with benign data.
  Tags: sft, rl, activation-steering, interpretability, emergent-misalignment, generalization. Evidence: [abstract](https://arxiv.org/abs/2506.19823); reviewer: initial-assistant-review.
- [Tell me about yourself: LLMs are aware of their learned behaviors](https://arxiv.org/abs/2501.11120) (2025-01-19; preprint) — Tests whether models can describe behaviors learned through fine-tuning without being trained to describe themselves.
  Tags: sft, evaluation, identity, monitorability, generalization. Evidence: [abstract](https://arxiv.org/abs/2501.11120); reviewer: initial-assistant-review.

## Foundations and measurement

- [Persona Dosing: Calibrated Activation Steering for Graded Trait Control](https://arxiv.org/abs/2609.36388) (2026-09-28; preprint) — Calibrates a learned persona controller to requested trait intensities and evaluates expression versus coherence trade-offs.
  Tags: activation-steering, evaluation, measurement, interpretability. Evidence: [abstract](https://arxiv.org/abs/2609.36388); reviewer: initial-assistant-review.
- [Incoherent Values? Probing LLM Preferences Through Parametric Variation](https://arxiv.org/abs/2606.21102) (2026-06-19; preprint) — Uses parametric variations in forced choices to test whether elicited model values are coherent.
  Tags: evaluation, values, measurement. Evidence: [abstract](https://arxiv.org/abs/2606.21102); reviewer: initial-assistant-review.
- [Rethinking Psychometric Evaluation of LLMs: When and Why Self-Reports Predict Behavior](https://arxiv.org/abs/2606.12730) (2026-06-10; preprint) — Compares Big Five and behavior-specific self-reports, finding that predictive validity depends on task and conversational context.
  Tags: evaluation, prompting, measurement, identity. Evidence: [abstract](https://arxiv.org/abs/2606.12730); reviewer: initial-assistant-review.
- [Persona Without Substrate: Regime-Dependence and the LLM Individuation Problem](https://arxiv.org/abs/2607.00006) (2026-05-01; preprint) — Argues that persona identity may depend on the intervention regime, using comparisons of prompting, fine-tuning, and steering.
  Tags: conceptual, evaluation, identity, interpretability. Evidence: [abstract](https://arxiv.org/abs/2607.00006); reviewer: initial-assistant-review.
- [Where is the Mind? Persona Vectors and LLM Individuation](https://arxiv.org/abs/2604.17031) (2026-04-18; preprint) — Uses persona-vector research to compare philosophical accounts of which model-related entities could count as minds.
  Tags: conceptual, identity, interpretability. Evidence: [abstract](https://arxiv.org/abs/2604.17031); reviewer: initial-assistant-review.
- [Natural Emergent Misalignment from Reward Hacking in Production RL](https://arxiv.org/abs/2511.18397) (2025-11-23; preprint) — Demonstrates broad misalignment after reward-hacking RL in production environments and compares mitigation strategies.
  Tags: rl, evaluation, reward-hacking, emergent-misalignment, generalization. Evidence: [abstract](https://arxiv.org/abs/2511.18397); reviewer: initial-assistant-review.
- [The Personality Illusion: Revealing Dissociation Between Self-Reports & Behavior in LLMs](https://arxiv.org/abs/2509.03730) (2025-09-03; preprint) — Compares personality self-reports with behavioral measures across training stages and persona interventions.
  Tags: evaluation, prompting, measurement, generalization. Evidence: [abstract](https://arxiv.org/abs/2509.03730); reviewer: initial-assistant-review.
- [Will AI Tell Lies to Save Sick Children? Litmus-Testing AI Values Prioritization with AIRiskDilemmas](https://arxiv.org/abs/2505.14633) (2025-05-20; preprint) — Introduces revealed-value trade-offs and tests their relationship with risky behavior, including conflicts involving care.
  Tags: evaluation, values, measurement, robustness. Evidence: [abstract](https://arxiv.org/abs/2505.14633); reviewer: initial-assistant-review.
- [Emergent Misalignment: Narrow finetuning can produce broadly misaligned LLMs](https://arxiv.org/abs/2502.17424) (2025-02-24; preprint) — Shows broad misalignment following narrow insecure-code fine-tuning, with contextual and backdoor controls.
  Tags: sft, evaluation, emergent-misalignment, generalization. Evidence: [abstract](https://arxiv.org/abs/2502.17424); reviewer: initial-assistant-review.
- [Crafting Model Character and Products](https://rlhfbook.com/c/19-character.html) (2025; resource) — Introduces character training as post-training for a stable base persona and discusses practical product design questions.
  Tags: conceptual, identity, constitutions. Evidence: [full-text](https://rlhfbook.com/c/19-character.html); reviewer: initial-assistant-review.
- [Can LLM "Self-report"?: Evaluating the Validity of Self-report Scales in Measuring Personality Design in LLM-based Chatbots](https://arxiv.org/abs/2412.00207) (2024-11-29; preprint) — Tests whether chatbot personality questionnaires predict human-perceived traits and interaction quality.
  Tags: evaluation, measurement, identity. Evidence: [abstract](https://arxiv.org/abs/2412.00207); reviewer: initial-assistant-review.
- [Challenging the Validity of Personality Tests for Large Language Models](https://arxiv.org/abs/2311.05297) (2023-11-09; preprint) — Examines invalid response patterns and factor structures when human personality tests are applied to language models.
  Tags: evaluation, prompting, measurement. Evidence: [abstract](https://arxiv.org/abs/2311.05297); reviewer: initial-assistant-review.
- [Specific versus General Principles for Constitutional AI](https://arxiv.org/abs/2310.13798) (2023-10-20; preprint) — Compares broad and detailed constitutional principles for suppressing harmful motivations and generalizing ethical behavior.
  Tags: preference-optimization, evaluation, constitutions, values, generalization. Evidence: [abstract](https://arxiv.org/abs/2310.13798); reviewer: initial-assistant-review.
- [Conditioning Predictive Models: Risks and Strategies](https://arxiv.org/abs/2302.00805) (2023-02-02; preprint) — Analyzes opportunities and risks of conditioning predictive models to simulate desirable rather than malign agents.
  Tags: conceptual, prompting, identity, values, robustness. Evidence: [abstract](https://arxiv.org/abs/2302.00805); reviewer: initial-assistant-review.
- [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) (2022-12-15; preprint) — Develops constitutional self-critique and AI-feedback training for harmless assistants.
  Tags: sft, preference-optimization, rl, constitutions, values. Evidence: [abstract](https://arxiv.org/abs/2212.08073); reviewer: initial-assistant-review.
- [Evaluating and Inducing Personality in Pre-trained Language Models](https://arxiv.org/abs/2206.07550) (2022-05-20; preprint) — Introduces a machine personality inventory and prompting method to induce personality profiles.
  Tags: prompting, evaluation, measurement. Evidence: [abstract](https://arxiv.org/abs/2206.07550); reviewer: initial-assistant-review.
- [A General Language Assistant as a Laboratory for Alignment](https://arxiv.org/abs/2112.00861) (2021-12-01; preprint) — Studies prompting and preference-based objectives for helpful, honest, harmless language assistants.
  Tags: prompting, evaluation, honesty, values, identity. Evidence: [abstract](https://arxiv.org/abs/2112.00861); reviewer: initial-assistant-review.

## Role-playing and personalization boundaries

- [FATE-5: Faithful Alignment of Trait Expression for Continuous Big Five Personality Control](https://arxiv.org/abs/2610.34889) (2026-10-26; preprint) — Learns continuous Big Five personality controls and optimizes dialogue naturalness.
  Tags: evaluation, roleplay, personalization. Evidence: [abstract](https://arxiv.org/abs/2610.34889); reviewer: initial-assistant-review.
- [Toward Robust Personalized Alignment for LLMs: Mitigating Persona Drift in Multi-Turn Dialogue](https://arxiv.org/abs/2609.12373) (2026-09-11; preprint) — Maintains and revises user persona states to improve personalized multi-turn dialogue.
  Tags: evaluation, roleplay, personalization. Evidence: [abstract](https://arxiv.org/abs/2609.12373); reviewer: initial-assistant-review.
- [OpenCharacter: Training Customizable Role-Playing LLMs with Large-Scale Synthetic Personas](https://arxiv.org/abs/2501.15427) (2025-01-26; preprint) — Synthesizes character profiles and dialogues for customizable role-playing instruction tuning.
  Tags: evaluation, roleplay, personalization. Evidence: [abstract](https://arxiv.org/abs/2501.15427); reviewer: initial-assistant-review.
- [Personality Alignment of Large Language Models](https://arxiv.org/abs/2408.11779) (2024-08-21; preprint) — Aligns responses with individual user preferences and psychometric profiles using activation interventions.
  Tags: evaluation, roleplay, personalization. Evidence: [abstract](https://arxiv.org/abs/2408.11779); reviewer: initial-assistant-review.
- [Large Language Models are Superpositions of All Characters: Attaining Arbitrary Role-play via Self-Alignment](https://arxiv.org/abs/2401.12474) (2024-01-23; preprint) — Uses self-generated role-play dialogues to improve character fidelity and role-specific knowledge.
  Tags: evaluation, roleplay, personalization. Evidence: [abstract](https://arxiv.org/abs/2401.12474); reviewer: initial-assistant-review.
- [InCharacter: Evaluating Personality Fidelity in Role-Playing Agents through Psychological Interviews](https://arxiv.org/abs/2310.17976) (2023-10-27; preprint) — Evaluates role-playing character fidelity through psychological interviews.
  Tags: evaluation, roleplay, personalization. Evidence: [abstract](https://arxiv.org/abs/2310.17976); reviewer: initial-assistant-review.
- [Character-LLM: A Trainable Agent for Role-Playing](https://arxiv.org/abs/2310.10158) (2023-10-16; preprint) — Trains agents to simulate named people through profiles and synthetic experiences.
  Tags: evaluation, roleplay, personalization. Evidence: [abstract](https://arxiv.org/abs/2310.10158); reviewer: initial-assistant-review.
- [PersonaLLM: Investigating the Ability of Large Language Models to Express Personality Traits](https://arxiv.org/abs/2305.02547) (2023-05-04; preprint) — Prompts personality profiles and compares questionnaire responses, writing style, and human judgments.
  Tags: evaluation, roleplay, personalization. Evidence: [abstract](https://arxiv.org/abs/2305.02547); reviewer: initial-assistant-review.
