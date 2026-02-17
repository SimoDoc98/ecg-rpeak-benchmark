# statistics/stats_offline.R

# --- ARGUMENT PARSING ---
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) {
  stop("Usage: Rscript stats_offline.R <input_csv> <output_xlsx>")
}
input_file <- args[1]
output_file <- args[2]

# --- PACKAGE INSTALLATION & LOADING ---
required_packages <- c("glmmTMB", "performance", "emmeans", "openxlsx", "dplyr")
new_packages <- required_packages[!(required_packages %in% installed.packages()[,"Package"])]
if(length(new_packages)) install.packages(new_packages, repos = "http://cran.us.r-project.org")

suppressPackageStartupMessages({
  library(glmmTMB)
  library(performance)
  library(emmeans)
  library(openxlsx)
  library(dplyr)
})

cat(">>> R: Loading offline benchmark data from", input_file, "\n")
df_off <- read.csv(input_file)

# --- PREPROCESSING ---
# Convert categorical variables to factors
df_off$Algorithm <- as.factor(df_off$Algorithm)
df_off$Participant <- as.factor(df_off$Participant)
df_off$Database <- as.factor(df_off$Database)

# Beta transformation for F1 and Jitter_F1 (Smithson & Verkuilen, 2006)
# Maps values to (0, 1) interval to satisfy Beta distribution constraints
n_off <- nrow(df_off)
df_off$F1_beta <- (df_off$F1 * (n_off - 1) + 0.5) / n_off
df_off$Jitter_F1_beta <- (df_off$Jitter_F1 * (n_off - 1) + 0.5) / n_off

cat(">>> R: Fitting GLMMs (Beta Family)...\n")

# --- GLMM MODELING ---

# 1. Model for F1-Score
model_F1_off <- glmmTMB(
  F1_beta ~ Algorithm + (1 | Database/Participant),
  data = df_off,
  family = beta_family(link = "logit")
)

# 2. Model for Jitter F1
model_JF_off <- glmmTMB(
  Jitter_F1_beta ~ Algorithm + (1 | Database/Participant),
  data = df_off,
  family = beta_family(link = "logit")
)

# --- FIT QUALITY METRICS ---
cat("--- Fit Quality (Conditional/Marginal R2) ---\n")
r2_f1 <- r2(model_F1_off)
r2_jf <- r2(model_JF_off)
cat(sprintf("F1: Cond R2=%.3f, Marg R2=%.3f\n", r2_f1$R2_conditional, r2_f1$R2_marginal))
cat(sprintf("JF: Cond R2=%.3f, Marg R2=%.3f\n", r2_jf$R2_conditional, r2_jf$R2_marginal))

# --- POST-HOC ANALYSIS ---
cat(">>> R: Computing Estimated Marginal Means (EMM) and Contrasts...\n")

# EMM Computation
emm_F1_off <- emmeans(model_F1_off, ~ Algorithm, type = "response")
emm_JF_off <- emmeans(model_JF_off, ~ Algorithm, type = "response")

# Pairwise Comparisons (Tukey adjusted)
posthoc_F1_off <- emmeans(model_F1_off, pairwise ~ Algorithm, type = "response")
posthoc_JF_off <- emmeans(model_JF_off, pairwise ~ Algorithm, type = "response")

# Extract contrasts as dataframes
posthoc_F1_off_df <- as.data.frame(posthoc_F1_off$contrasts)
posthoc_JF_off_df <- as.data.frame(posthoc_JF_off$contrasts)

# --- EXPORT TO EXCEL ---
cat(">>> R: Saving results to", output_file, "\n")
wb_off <- createWorkbook()

addWorksheet(wb_off, "EMM_F1")
writeData(wb_off, "EMM_F1", as.data.frame(emm_F1_off))

addWorksheet(wb_off, "EMM_Jitter_F1")
writeData(wb_off, "EMM_Jitter_F1", as.data.frame(emm_JF_off))

addWorksheet(wb_off, "PostHoc_F1")
writeData(wb_off, "PostHoc_F1", posthoc_F1_off_df)

addWorksheet(wb_off, "PostHoc_Jitter_F1")
writeData(wb_off, "PostHoc_Jitter_F1", posthoc_JF_off_df)

saveWorkbook(wb_off, output_file, overwrite = TRUE)
cat(">>> R: Offline Analysis Complete.\n")