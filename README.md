# Ranking the Power 4: A Data-Driven Look at Conference Strength

Conference strength is one of the most debated topics in college football, but it’s often driven by reputation rather than data. In this analysis, I focus on head-to-head matchups between Power conferences to evaluate not just who wins, but how meaningful those wins are. By weighting victories based on the quality of the opponent, this approach offers a more objective way to assess which conferences are actually performing at the highest level, and which ones may be overrated.

### Ranking within Conferences

To assess the value of individual wins, I first ranked each team within its respective conference based on intra-conference performance. This provides a relative measure of team strength within each league. The idea is that a win over a top-tier team carries more weight than a win over a bottom-tier one. So, if a lower-ranked team in Conference A beats a high-ranked team in Conference B, that result is treated as more impactful than the reverse. This method does assume some equivalence between similarly ranked teams across conferences—for example, that the No. 1 team in Conference A is roughly comparable in strength to the No. 1 team in Conference B—though that isn’t always the case. As a next step, I plan to explore more precise ways to evaluate the impact of individual wins. The rankings are then normalized to allow fair comparison across conferences.

![[docs/Preprocessing Step.png]]

$$\text{Norm Rank} = \frac{1}{n^{\alpha}}$$
$$\text{Norm Rank} \in (0,1] \subset \mathbb{R}$$

**Aside**: $\alpha$ is a smoothing factor to avoid rapid decrease in the Normalized Rank. Should $\alpha = 1$ (as would be the case if no $\alpha$ was used) then the decrease would be $1, 0.5, 0.25, ...$. This is too drastic and will make later calculations less meaningful. I found experimentally that $\alpha = 0.5$ worked well.

#### Ranking Results:

**SEC**

| Team               | Value   |
|--------------------|---------|
| Georgia            | 1.000   |
| Texas              | 0.707   |
| Tennessee          | 0.577   |
| Alabama            | 0.500   |
| Texas A&M          | 0.447   |
| Missouri           | 0.408   |
| LSU                | 0.378   |
| Ole Miss           | 0.354   |
| South Carolina     | 0.333   |
| Florida            | 0.316   |
| Arkansas           | 0.302   |
| Vanderbilt         | 0.289   |
| Auburn             | 0.277   |
| Oklahoma           | 0.267   |
| Kentucky           | 0.258   |
| Mississippi State  | 0.250   |

**ACC**

| Team           | Value |
| -------------- | ----- |
| SMU            | 1.000 |
| Clemson        | 0.707 |
| Miami          | 0.577 |
| Georgia Tech   | 0.500 |
| Duke           | 0.447 |
| Syracuse       | 0.408 |
| Louisville     | 0.378 |
| Virginia Tech  | 0.354 |
| Boston College | 0.333 |
| Pittsburgh     | 0.316 |
| Virginia       | 0.302 |
| North Carolina | 0.289 |
| NC State       | 0.277 |
| Wake Forest    | 0.267 |
| California     | 0.258 |
| Stanford       | 0.250 |
| Florida State  | 0.243 |

**Big Ten**

| Team             | Value   |
|------------------|---------|
| Oregon           | 1.000   |
| Indiana          | 0.707   |
| Penn State       | 0.577   |
| Ohio State       | 0.500   |
| Iowa             | 0.447   |
| Illinois         | 0.408   |
| Minnesota        | 0.378   |
| Michigan         | 0.354   |
| USC              | 0.333   |
| Rutgers          | 0.316   |
| Washington       | 0.302   |
| Wisconsin        | 0.289   |
| Nebraska         | 0.277   |
| Michigan State   | 0.267   |
| UCLA             | 0.258   |
| Northwestern     | 0.250   |
| Maryland         | 0.243   |
| Purdue           | 0.236   |

**Big 12**

| Team             | Value   |
|------------------|---------|
| Arizona State    | 1.000   |
| BYU              | 0.707   |
| Colorado         | 0.577   |
| Iowa State       | 0.500   |
| Baylor           | 0.447   |
| TCU              | 0.408   |
| Texas Tech       | 0.378   |
| West Virginia    | 0.354   |
| Kansas State     | 0.333   |
| Kansas           | 0.316   |
| Houston          | 0.302   |
| Cincinnati       | 0.289   |
| Arizona          | 0.277   |
| UCF              | 0.267   |
| Utah             | 0.258   |
| Oklahoma State   | 0.250   |

### Scoring Conferences

With normalized team rankings established, the next step is to score each game by comparing the ranks of the winner and loser. To prevent double counting, only the winner’s points contribute to their conference’s total score.

$$\text{Points for Winner} = \frac{\text{rank}_{\text{loser}}}{\text{rank}_{\text{winner}}}$$
This formula rewards upsets. Wins by lower-ranked teams over higher-ranked ones carry more weight, while expected wins by top teams over weaker opponents contribute less.

A known limitation is the assumption that similarly ranked teams across conferences are equally strong, which may not always be accurate. Refinements to this will be explored in future work.

### Results

The results of this analysis rank the conferences as follows: SEC first, followed by the Big Ten, then the ACC, and finally the Big 12. This generally aligns with the consensus within the college football community, although some might argue the ACC and Big 12 should be switched. Interestingly, the ACC and Big 12 are nearly neck and neck, while the SEC and Big Ten hold a clear lead over the rest.

With the 2025 college football season just around the corner, I’m excited to see how this year’s interconference matchups will impact these rankings.

![[docs/Final Results Plot.png]]

### Future Work and Acknowledgements

The [College Football Data API](https://collegefootballdata.com/) provided the historical game data used for this analysis.

Moving forward, I plan to refine the team ranking process by incorporating margins of victory and detailed game statistics. This will create a more nuanced metric for evaluating individual wins. Additionally, I aim to apply similar statistical considerations when scoring head-to-head matchups, improving the accuracy of conference comparisons.