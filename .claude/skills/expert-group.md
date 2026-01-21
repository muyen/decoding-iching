# Expert Group Analysis Skill

**Name:** expert-group
**Trigger:** /expert-group [topic]
**Description:** Invoke multiple expert perspectives to analyze a problem from different angles

## Usage

```
/expert-group <topic or question>
```

## Expert Roles

This skill spawns multiple specialized agents in parallel to provide diverse perspectives:

### 1. Domain Expert
- For technical topics: Relevant domain specialist
- For I Ching: 易經大師 (I Ching Master)
- For code: Software Architect
- Provides deep domain knowledge and traditional wisdom

### 2. Mathematician
- Number theory and sequence analysis
- Pattern recognition in numerical data
- Algebraic structures and group theory
- Statistical foundations

### 3. Pattern Recognition Expert
- Signal processing and image analysis
- Sequence pattern detection
- Autocorrelation and frequency analysis
- Clustering and classification

### 4. Statistician
- Hypothesis testing
- Bayesian inference
- Time series analysis
- Effect size and significance

### 5. Algorithm Expert
- Data structures optimization
- Computational complexity
- Encoding and compression
- Algorithm design

### 6. Computer Scientist
- Machine learning approaches
- Information theory
- Computational models
- Data mining techniques

## Execution Steps

1. **Parse Topic**: Extract the main subject and context from user input

2. **Select Relevant Experts**: Based on the topic, select 4-6 most relevant expert perspectives

3. **Launch Parallel Agents**: Use Task tool to spawn all expert agents simultaneously

4. **Collect Results**: Wait for all agents to complete

5. **Synthesize Insights**: Create unified report combining all perspectives

6. **Identify Consensus**: Highlight areas of agreement across experts

7. **Note Conflicts**: Document where experts disagree and why

8. **Generate Recommendations**: Actionable next steps based on expert synthesis

## Output Format

```markdown
# Expert Group Analysis: [Topic]

## Executive Summary
[2-3 sentence overview]

## Expert Perspectives

### [Expert Type 1]
**Key Insights:**
- [Point 1]
- [Point 2]

**Suggested Approaches:**
- [Approach 1]
- [Approach 2]

### [Expert Type 2]
[Same format...]

## Consensus Points
- [Agreement 1]
- [Agreement 2]

## Areas of Divergence
| Topic | Expert A View | Expert B View |
|-------|--------------|---------------|
| ... | ... | ... |

## Recommended Next Steps
1. [Action 1]
2. [Action 2]
3. [Action 3]

## Questions for Further Investigation
- [Question 1]
- [Question 2]
```

## Example Invocations

### Research Problem
```
/expert-group "What patterns exist in the I Ching's 384 yaos that determine 吉凶?"
```

### Technical Decision
```
/expert-group "Should we use microservices or monolith for our e-commerce platform?"
```

### Data Analysis
```
/expert-group "Analyze the user engagement data to find optimization opportunities"
```

## Implementation Notes

- Always launch at least 4 expert agents in parallel for comprehensive coverage
- Include at least one quantitative expert (mathematician/statistician) and one qualitative expert (domain/design)
- Time limit: Allow 2-3 minutes for complex analyses
- Prioritize actionable insights over theoretical completeness
