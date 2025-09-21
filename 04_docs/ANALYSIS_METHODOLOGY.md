# TikTok Analysis Methodology Documentation

## Current Status: Methodology Review & Enhancement

**Date**: August 3, 2025  
**Issue Identified**: Initial analysis made claims without sufficient statistical validation  
**Action**: Implementing rigorous exploratory data analysis before drawing conclusions

## Problems with Initial Approach

### 1. **Superficial Categorization**
- **Issue**: Grouped videos by simple keyword matching (e.g., "yoga" in caption = yoga category)
- **Problem**: Videos may be miscategorized based on hashtags vs actual content
- **Example**: A strength training video tagged #yoga for reach would be misclassified

### 2. **Insufficient Statistical Validation**
- **Issue**: Claimed "Yoga/Pilates drives highest engagement at 6.5%" without checking sample sizes or outliers
- **Problem**: 87 yoga videos vs 553 strength videos - not comparable samples
- **Missing**: Statistical significance testing, confidence intervals

### 3. **Creator Bias Not Accounted For**
- **Issue**: Category averages could be skewed by individual high-performing creators
- **Example**: If one viral yoga creator has 10 videos, they could inflate the entire yoga category average
- **Missing**: Creator influence analysis, outlier detection

### 4. **Unvalidated Claims**
- **Issue**: Statements like "Women's content drives 9% higher engagement" need deeper investigation
- **Problem**: Could be confounded by creator popularity, content type, timing, or other factors
- **Missing**: Controlled analysis accounting for confounding variables

## Revised Rigorous Methodology

### Phase 1: Data Exploration & Quality Assessment

#### **1.1 Distribution Analysis**
- Plot engagement rate distributions across all videos
- Identify natural clusters or patterns in the data
- Understand the shape of performance distributions
- **Goal**: Find genuine patterns rather than imposing categories

#### **1.2 Outlier Detection**
- Identify videos with unusually high/low engagement
- Map outliers to specific creators
- Assess how outliers impact category averages
- **Goal**: Separate genuine trends from individual viral content

#### **1.3 Sample Size Validation**
- Calculate minimum sample sizes needed for statistical significance
- Flag categories with insufficient data for reliable conclusions
- **Threshold**: Minimum 30 videos per category for basic analysis, 100+ for robust conclusions

#### **1.4 Creator Influence Mapping**
- Measure how much each creator influences their category's average
- Identify categories dominated by single creators
- Calculate engagement rates with and without top performers
- **Goal**: Distinguish creator effects from content type effects

### Phase 2: Pattern Discovery

#### **2.1 Hypothesis Generation**
- Examine top-performing content without preconceived categories
- Look for genuine patterns in:
  - Content format (duration, style, production quality)
  - Timing (posting patterns, seasonal effects)
  - Audience targeting (demographics, interests)
  - Creator characteristics (follower count, verification, consistency)

#### **2.2 Statistical Testing**
- Use appropriate statistical tests for comparing groups (t-tests, ANOVA, Chi-square)
- Calculate effect sizes, not just p-values
- Account for multiple comparisons (Bonferroni correction)
- **Goal**: Only claim differences that are statistically meaningful

#### **2.3 Confounding Variable Analysis**
- Control for creator popularity when comparing content types
- Account for posting timing and viral trends
- Separate correlation from causation
- **Goal**: Isolate the true drivers of engagement

### Phase 3: Validated Insights

#### **3.1 Confidence Levels**
- **High Confidence**: Large samples (100+ videos), significant p-values (<0.01), large effect sizes
- **Medium Confidence**: Moderate samples (30-100 videos), significant p-values (<0.05), medium effect sizes  
- **Low Confidence/Exploratory**: Small samples (<30 videos), trends only, requires more data

#### **3.2 Bias Documentation**
- Clearly flag when results are influenced by outliers or specific creators
- Provide both "with outliers" and "without outliers" analyses
- Document all limitations and caveats
- **Goal**: Full transparency about analytical limitations

#### **3.3 Actionable Recommendations**
- Only make business recommendations for High Confidence findings
- Provide specific next steps for Medium Confidence trends
- Frame Low Confidence insights as hypotheses for further investigation

## Key Questions to Answer Rigorously

1. **What content characteristics actually drive engagement?** (not just category labels)
2. **Which patterns are driven by content vs creator popularity?**
3. **What sample sizes do we have for reliable conclusions?**
4. **Which differences are statistically significant and practically meaningful?**
5. **What are the confidence levels for each claimed insight?**

## Deliverables from Rigorous Analysis

1. **Statistical validation report** - Confidence levels for all claims
2. **Outlier analysis** - Creator bias documentation  
3. **Pattern discovery findings** - Data-driven insights (not assumption-driven)
4. **Actionable recommendations** - Only for statistically validated findings
5. **Exploratory hypotheses** - Areas requiring more investigation

## Success Criteria

- **No claims without statistical backing**
- **Clear documentation of limitations**  
- **Transparent methodology throughout**
- **Actionable insights based on robust patterns**
- **Centr can confidently act on findings**

---

*This methodology ensures that Centr's strategic decisions are based on rigorous analysis rather than superficial pattern matching.*