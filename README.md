# Academic Projects

Academic implementations, experiments and engineering projects, organized by topic.
My main interests are **machine learning, AI engineering and research**. The collection
also includes the statistics, algorithms and data engineering that support this work.

## Selected work

| Work | What to look for | Evidence and limitations |
| --- | --- | --- |
| [Active Learning](machine-learning/active-learning/) | Acquiring useful labels under a budget; handling rare positive examples. | Documented comparisons and seed variability; course data are required for reproduction. |
| [Surgical Tool Detection](computer-vision/surgical-tool-detection/) | Baseline training and pseudo-label experiments, including distribution shift. | Validation gains did not imply OOD gains; the documented final choice is the baseline. See its experiment matrix and reproduction guide. |

Other substantial work includes [entity matching](machine-learning/entity-matching/),
[hybrid Wikipedia retrieval](information-retrieval/wikipedia-hybrid-retrieval/) and
[adversarial/contrastive learning](deep-learning/adversarial-and-contrastive-learning/).
Their READMEs distinguish implementation from historical, unrerun results.

## Topics and skills

| Topic | Contents |
| --- | --- |
| [Machine learning](machine-learning/) | Active learning, entity matching, KNN, perceptron, K-means, Spark classification, sparse recommendation and budgeted UCB. |
| [Deep learning](deep-learning/) | Manual backpropagation with PyTorch tensors, CNNs, random-label memorization, IMDB RNN/LSTM, FGSM, SimCLR, VAE and GraphSAGE. |
| [Computer vision](computer-vision/) | Surgical tool detection and experiments with pseudo-labels. |
| [Information retrieval](information-retrieval/) | Boolean search, feedback models, an exact dynamic vector index, hybrid retrieval and a MAP optimization case study. |
| [AI and decision making](ai-and-decision-making/) | LLM orchestration, heuristic search, partial observability, stochastic planning, network influence and GSP auction agents. |
| [Statistics](statistics/) | EDA, inference, regression/model selection and bootstrap. |
| [Engineering foundations](engineering-foundations/) | Data pipelines, Spark/MapReduce, SQL/Django, Java OOP, C and an xv6 patch. |

Small exercises are grouped as coursework rather than presented as separate highlights.
Code is stored once; related topics link to each other.

## Reading and running the repository

Start with an individual project's README. Projects have different datasets and runtimes;
this is not a single application with a shared installation command. Some require
Databricks, course scaffolding, external services or excluded weights/data.

Course task descriptions, checker interfaces and supplied frameworks are credited in
the project READMEs. Imported notebooks have had execution outputs, embedded submission
images and user metadata removed from the public copy. Written historical analyses
remain, but their numbers are not new independent benchmark results.

See [validation and known limitations](docs/VALIDATION.md) and
[publication hygiene](docs/PUBLICATION.md). Run the small local regression suite with
`python -m pytest tests -q` after installing `tests/requirements.txt`.
