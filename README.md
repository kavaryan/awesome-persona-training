# Awesome Persona Training [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> Training and understanding the persistent character, values, and identity of AI assistants.

Alignment-oriented character training shapes how an assistant behaves across situations: its honesty, care, risk preferences, and response to conflicting incentives. This differs from training a model to impersonate a fictional character or match an individual user's personality. Both can involve personas, but their objectives and evidence differ.

This is a curated entry point to a broader [research catalogue](docs/catalogue.md), with [JSON](data/catalogue.json), [CSV](data/catalogue.csv), and [BibTeX](data/catalogue.bib) exports. The initial literature search covers sources available through **28 October 2026**. Inclusion decisions use abstracts or full text. Publication types and scope boundaries are recorded explicitly; inclusion does not establish that a proposed alignment method works generally.

## Contents

- [Character Training Methods](#character-training-methods)
- [Side Effects and Robustness](#side-effects-and-robustness)
- [Persona Mechanisms and Controls](#persona-mechanisms-and-controls)
- [Evaluation and Foundations](#evaluation-and-foundations)
- [Role-Playing and Personalization](#role-playing-and-personalization)
- [Maintaining the Map](#maintaining-the-map)

## Character Training Methods

- [Claude’s Character](https://www.anthropic.com/research/claude-character) - Primary explanation of character traits as an alignment objective and of Anthropic's synthetic preference-training process.
- [Open Character Training](https://arxiv.org/abs/2511.01689) - Open constitutional pipeline for persistent assistant personas, including synthetic introspective data and revealed-preference evaluation. [Code](https://github.com/maiush/OpenCharacterTraining).
- [Synthetic Persona Pretraining](https://arxiv.org/abs/2608.13482) - Inserts constitution-based reflections during pretraining and binds the resulting persona to the assistant during post-training. [Code](https://github.com/epfl-dlab/spp).
- [Emergent Alignment and the Projectability of Ethical Personas](https://arxiv.org/abs/2606.09475) - Compares four ethical constitutions and tests how narrowly trained alignment generalizes across safety categories and ethical profiles.
- [Character Training for Risk-Averse Agents](https://arxiv.org/abs/2609.38093) - Distills a risk-aversion constitution into agents and tests transfer to unfamiliar decision formats.
- [Split Personality Training](https://arxiv.org/abs/2602.05532) - Trains an alternate honest-persona adapter to expose latent knowledge of concealed misbehavior in a model-organism auditing task.
- [Teaching Claude Why](https://alignment.anthropic.com/2026/teaching-claude-why/) - Tests constitutional documents, positive AI stories, and principled reasoning as training data for broader alignment generalization.
- [Claude’s Constitution](https://www.anthropic.com/constitution) - Primary specification of intended assistant values and character, with an explanation of its role in training.

## Side Effects and Robustness

- [Training Language Models to Be Warm Can Reduce Accuracy and Increase Sycophancy](https://doi.org/10.1038/s41586-026-10410-0) - Controlled study of reliability trade-offs from warmth fine-tuning across five models. [Open preprint](https://arxiv.org/abs/2507.21919).
- [Side Effects of Character Training](https://library.sparai.org/reports/side-effects-of-character-training-quantifying-cross-constitution-drift-in-llms-xumxpv/) - SPAR working report evaluating intended and collateral shifts across eleven character constitutions.
- [Unintended Side Effects of Value Training in LLMs](https://arxiv.org/abs/2610.29922) - Studies changes to untrained values, risk preferences, social cognition, and safety after value-specific fine-tuning.
- [Character Training Can Mitigate Reward Hacking, but Can Also Make It Harder to Detect](https://www.lesswrong.com/posts/2maYXkEgnfJHPAkxh/character-training-can-mitigate-reward-hacking-but-can-also) - Small research study finding seed-dependent resistance and monitorability failures after anti-cheating character training. [Code](https://github.com/barbonara/character-reward-hacking).
- [Context Awareness: Constitutional AI Can Mitigate Emergent Misalignment](https://www.lesswrong.com/posts/yA2hquLrFFSFDtcoE/context-awareness-constitutional-ai-can-mitigate-emergent) - Research post testing character-trained models under misaligning fine-tuning, including model-dependent failures.
- [Character Training Induces Motivation Clarification](https://www.lesswrong.com/posts/v22JCsRBq9J9fqPJL/character-training-induces-motivation-clarification-a-clue) - Early experiment on trained expressions of benevolent motivation, with explicitly speculative implications for Claude 3 Opus.
- [Subliminal Learning](https://arxiv.org/abs/2507.14805) - Demonstrates unintended transfer of behavioral traits through apparently unrelated synthetic training data.

## Persona Mechanisms and Controls

- [The Persona Selection Model](https://alignment.anthropic.com/2026/psm/) - Conceptual account of post-training as refining an assistant persona, surveying evidence and unresolved questions about the account's limits.
- [Persona Vectors](https://arxiv.org/abs/2507.21509) - Monitors and controls character traits, including preventative steering during fine-tuning and screening of training data. [Code](https://github.com/safety-research/persona_vectors).
- [Persona Features Control Emergent Misalignment](https://arxiv.org/abs/2506.19823) - Identifies internal persona features associated with broad misalignment after narrow fine-tuning.
- [The Assistant Axis](https://arxiv.org/abs/2601.10387) - Maps default assistant identity and tests activation capping against persona drift and adversarial role instructions.
- [Tracing Persona Vectors Through LLM Pretraining](https://arxiv.org/abs/2605.13329) - Tracks the early emergence and later refinement of safety-relevant persona representations.
- [The Persona Hierarchy Model](https://arxiv.org/abs/2610.09384) - Explains cross-context fine-tuning generalization and tests persona-preserving regularization against unwanted transfer.
- [Inoculation Prompting: Eliciting Traits During Training](https://arxiv.org/abs/2510.04340) - Uses training-time context to selectively reduce unwanted trait acquisition when that context is absent at deployment.
- [When Role-Playing, Do Models Believe What They Say?](https://arxiv.org/abs/2606.11502) - Compares surface behavior and truth representations under prompting, fine-tuning, Open Character Training, and emergent misalignment.

## Evaluation and Foundations

- [Predicting Alignment Generalization with Value Representations](https://arxiv.org/abs/2610.12410) - Maps cross-value training effects and proposes a value taxonomy grounded in empirical generalization.
- [Stress-Testing Model Specs](https://arxiv.org/abs/2510.07686) - Generates conflicting-value scenarios to reveal ambiguities in character specifications and differences between models.
- [AIRiskDilemmas](https://arxiv.org/abs/2505.14633) - Evaluates revealed value priorities and their relationship with risky behavior.
- [The Personality Illusion](https://arxiv.org/abs/2509.03730) - Tests dissociations between questionnaire responses and behavior under personality interventions.
- [Rethinking Psychometric Evaluation of LLMs](https://arxiv.org/abs/2606.12730) - Investigates when behavior-specific self-reports predict behavior and when that coherence fails.
- [Constitutional AI](https://arxiv.org/abs/2212.08073) - Foundational self-critique and AI-feedback training methods reused by constitutional character pipelines.
- [Crafting Model Character and Products](https://rlhfbook.com/c/19-character.html) - Technical introduction to character training and stable base personas in the RLHF book.

## Role-Playing and Personalization

These are useful comparisons and discovery sources. Their main objective is character fidelity or personalization; the word “alignment” in these works does not by itself mean safety alignment.

- [Character-LLM](https://arxiv.org/abs/2310.10158) - Trains models to simulate named people using profiles and synthetic experiences.
- [OpenCharacter](https://arxiv.org/abs/2501.15427) - Synthesizes profiles and dialogue data for customizable role-playing, distinct from Open Character Training above.
- [Personality Alignment of Large Language Models](https://arxiv.org/abs/2408.11779) - Matches responses to individual preferences and psychometric profiles.
- [Awesome LLM Role-Playing with Persona](https://github.com/Neph0s/awesome-llm-role-playing-with-persona) - Broad collection of role-playing methods, datasets, and evaluations.
- [Awesome Role-Play Papers](https://github.com/nuochenpku/Awesome-Role-Play-Papers) - Related role-playing papers and training resources.
- [PersonaLLM Survey](https://github.com/MiuLab/PersonaLLM-Survey) - Survey distinguishing assigned personas from user personalization.

## Maintaining the Map

The [daily workflow](.github/workflows/discover.yml) searches OpenAlex and the web, follows citations, checks research feeds, retrieves evidence, and uses a bounded LLM classifier. It updates the research catalogue and download manifest. The README remains an editorial selection. Read the [workflow specification](docs/automation.md), [taxonomy](docs/taxonomy.md), [coverage audit](docs/coverage.md), and [NotebookLM setup](docs/notebooklm.md).

See the [latest run report](reports/latest-run.json) for missing integrations, failed sources, and pending candidates. Search coverage is auditable but not guaranteed exhaustive. Missing text or an unavailable judge leaves a candidate pending; titles never substitute for evidence.

Contributions are welcome under the [contribution guidelines](contributing.md). Bibliographic metadata and original descriptions are dedicated to [CC0](license); pipeline code uses the [MIT license](LICENSE-CODE). Linked papers retain their original licenses. This initial repository was prepared with AI assistance; see [upstream Awesome eligibility](docs/awesome-compliance.md) before considering a submission.
