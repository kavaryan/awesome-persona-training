# Scope and tagging

The machine-readable vocabulary is [config/taxonomy.json](../config/taxonomy.json). Scope and intervention are separate: a paper can be central to character alignment while evaluating rather than training models.

| Scope | Inclusion rule | Examples |
| --- | --- | --- |
| `core` | Trains, specifies, or directly evaluates persistent assistant character, values, dispositions, or their safety consequences. | Open Character Training; warmth side effects; constitutions; cross-value drift. |
| `mechanism` | Explains or controls alignment-relevant persona selection, representations, transfer, or robustness. | Persona vectors; Assistant Axis; inoculation; default-persona generalization. |
| `background` | Enables understanding or measurement, with a documented character connection. | Constitutional AI; questionnaire validity; revealed values. |
| `roleplay` | Primarily targets assigned character fidelity or individual user personalization. | Character-LLM; OpenCharacter; Personality Alignment. |
| `exclude` | No substantive contribution to the topic. | Human character education; optical character recognition; generic dialogue applications. |
| `uncertain` | Evidence is missing, insufficient, or ambiguous. | A promising title with no abstract; a search results page; incomplete source text. |

An explicit safety experiment can make a role-playing paper a `mechanism` entry. Merely using the word “alignment” cannot. Fictional characters used to test persona-selection hypotheses are not automatically excluded. Conversely, a general RLHF paper does not become core merely because assistants have personas.

Intervention tags distinguish pretraining, SFT, preference optimization, RL, distillation, activation steering, prompting, data curation, evaluation, and conceptual work. Inference-time prompting and steering must not be described as changes learned in the model weights. Theme tags capture constitutions, values, honesty, sycophancy, warmth, reward hacking, monitorability, emergent misalignment, generalization, robustness, interpretability, identity, measurement, role-play, personalization, and subliminal transfer.

Each accepted record has a summary, boundary rationale, source type, abstract/full-text URL, retrieval date, content hash, short supporting quotation, and reviewer. Automated decisions also store the model, prompt version, confidence, and hash of the actual text supplied to the judge. These confidence values are model judgments, not calibrated probabilities. Automated additions are accepted only at a threshold of 0.90 and remain distinguishable from the initial editorial pass. A high confidence score does not imply a study's findings are reliable.

Use `evidence_type` for publication status, not quality rankings. Preprints, working reports, research posts, conceptual posts, and specifications remain distinguishable. Versions and code links belong in the same work record when their relationship is verified. For example, the warmth paper's Nature version and earlier arXiv version share one entry; descriptions avoid mixing their numerical results.
