
library(lme4)
library(lmerTest)
library(dplyr)
library(glmmTMB)
library(performance)

# ---- Load the CSV ----
df <- read.csv("/Users/tuu96099/Documents/GitHub/sliders-display-dashboard/analysis/study_export_no_slider_use_vs_control_no_soccer.csv")
df$Condition <- relevel(factor(df$Condition), ref = "control")
df$Participant.ID <- factor(df$Participant.ID)
df$Task.ID <- factor(df$Task.ID)

# # === Correctness (GLMM) ===
# cat("\n=== Correctness (GLMM) ===\n")
# model <- glmer(Success ~ Condition + (1|Participant.ID) + (1|Task.ID),
#                data = df,
#                family = binomial)
# print(summary(model))
# 
# # Fixed effects in % form
# cat("\n=== Correctness in % Form (GLMM) ===\n")
# logodds_to_acc <- function(log_odds) {
#   exp(log_odds) / (1 + exp(log_odds))
# }
# intercept <- fixef(model)["(Intercept)"]
# baseline_acc <- logodds_to_acc(intercept)
# cat(sprintf("%-20s  Estimate   Accuracy\n", "Parameter"))
# cat(strrep("-", 45), "\n")
# cat(sprintf("%-20s  %7.4f    %.1f%% (baseline: control)\n",
#             "(Intercept)", intercept, baseline_acc * 100))
# for (name in names(fixef(model))[-1]) {
#   coef_val <- fixef(model)[name]
#   acc <- logodds_to_acc(intercept + coef_val)
#   delta <- acc - baseline_acc
#   cat(sprintf("%-20s  %7.4f    %.1f%% (%+.1f%% vs baseline)\n",
#               name, coef_val, acc * 100, delta * 100))
# }


# # === Response Time (LMM) ===
# df$log_duration <- log(df$Duration)
# cat("\n=== Response Time (LMM) ===\n")
# model_time <- lmer(log_duration ~ Condition + (1|Participant.ID) + (1|Task.ID), data = df)
# print(summary(model_time))
# # === Response Time in Seconds ===
# cat("\n=== Response Time in Seconds (LMM) ===\n")
# intercept <- fixef(model_time)["(Intercept)"]
# slider_coef <- fixef(model_time)["Conditionslider"]
# control_sec <- exp(intercept)
# slider_sec <- exp(intercept + slider_coef)
# cat(sprintf("Control: %.2f sec\n", control_sec))
# cat(sprintf("Slider:  %.2f sec\n", slider_sec))
# cat(sprintf("Difference: %+.2f sec vs control\n", slider_sec - control_sec))


# cat("\n=== Starting Rank (LMM) ===\n")
# df$log_starting_rank <- log(df$Starting.Rank)
# model_starting_rank <- lmer(log_starting_rank ~ Condition + (1|Participant.ID) + (1|Task.ID), data = df)
# print(summary(model_starting_rank))
# 
# cat("\n=== Starting Rank by Condition ===\n")
# intercept <- fixef(model_starting_rank)["(Intercept)"]
# slider_coef <- fixef(model_starting_rank)["Conditionslider"]
# control_rank <- exp(intercept)
# slider_rank <- exp(intercept + slider_coef)
# cat(sprintf("Control: %.1f\n", control_rank))
# cat(sprintf("Slider:  %.1f\n", slider_rank))
# cat(sprintf("Difference: %+.1f vs control\n", slider_rank - control_rank))


# cat("\n=== Final Rank (LMM) ===\n")
# df$log_rank <- log(df$Final.Rank)
# model_rank <- lmer(log_rank ~ Condition + (1|Participant.ID) + (1|Task.ID), data = df)
# print(summary(model_rank))
# 
# cat("\n=== Final Rank by Condition ===\n")
# intercept <- fixef(model_rank)["(Intercept)"]
# slider_coef <- fixef(model_rank)["Conditionslider"]
# control_rank <- exp(intercept)
# slider_rank <- exp(intercept + slider_coef)
# cat(sprintf("Control: %.1f\n", control_rank))
# cat(sprintf("Slider:  %.1f\n", slider_rank))
# cat(sprintf("Difference: %+.1f vs control\n", slider_rank - control_rank))

# # === Query Searches (Poisson GLMM) ===
# cat("\n=== Query Searches (Poisson GLMM) ===\n")
# model_q_pois <- glmer(Query.Searches ~ Condition + (1|Participant.ID) + (1|Task.ID),
#                       family = poisson, data = df)
# print(summary(model_q_pois)$coefficients)
# check_overdispersion(model_q_pois)
# cat("\n=== Query Searches by Condition ===\n")
# i <- fixef(model_q_pois)["(Intercept)"]; s <- fixef(model_q_pois)["Conditionslider"]
# cat(sprintf("Control: %.2f | Slider: %.2f | Diff: %+.2f\n", exp(i), exp(i+s), exp(i+s)-exp(i)))

# slider_df <- df %>% filter(Condition == "slider")
# cat(sprintf("Slider-condition rows: %d\n", nrow(slider_df)))
# 
# 
# # === Slider Interactions Effect on Success ===
# cat("\n=== Slider Interactions -> Success (GLMM) ===\n")
# model_su_success <- glmer(Success ~ Slider.Interactions + (1|Participant.ID) + (1|Task.ID),
#                           family = binomial, data = slider_df)
# print(summary(model_su_success)$coefficients)
# 
# # === In odds-ratio / percentage form ===
# cat("\n=== Slider Interactions effect on odds of Success (%) ===\n")
# coef_val <- fixef(model_su_success)["Slider.Interactions"]
# odds_ratio <- exp(coef_val)
# pct_change <- (odds_ratio - 1) * 100
# cat(sprintf("Each slider move changes odds of success by %+.1f%%\n", pct_change))

# df <- read.csv("/Users/tuu96099/Documents/GitHub/sliders-display-dashboard/analysis/tlx_data.csv")
# df$Condition <- factor(df$Condition)
# 
# tlx_fields <- c("mental", "temporal", "performance", "effort", "frustration")
# cat("\n=== NASA-TLX Comparison (T-Test) ===\n")
# for (field in tlx_fields) {
#   t <- t.test(df[[field]] ~ df$Condition)
#   means <- t$estimate
#   cat(sprintf("%-12s control=%.2f  slider=%.2f  diff=%+.2f  p=%.4f  %s\n",
#               field, means[1], means[2], means[2]-means[1], t$p.value,
#               ifelse(t$p.value < 0.05, "*", "")))
# }
# 
#  