# statistics/stats_online.R

# --- ARGUMENT PARSING ---
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) {
  stop("Usage: Rscript stats_online.R <input_csv> <output_xlsx>")
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

cat(">>> R: Loading online benchmark data from", input_file, "\n")
df_on <- read.csv(input_file)

# --- PREPROCESSING ---
# Convert categorical variables to factors
df_on$Algorithm <- as.factor(df_on$Algorithm)
df_on$Participant <- as.factor(df_on$Participant)
df_on$Window_Sec <- as.factor(df_on$Window_Sec) # Treat window size as factor/categorical
df_on$Database <- as.factor(df_on$Database)

# Data Transformations
n_on <- nrow(df_on)
# Beta transformation for metrics (0,1 range)
df_on$F1_beta <- (df_on$F1 * (n_on - 1) + 0.5) / n_on
df_on$Jitter_F1_beta <- (df_on$Jitter_F1 * (n_on - 1) + 0.5) / n_on
# Gamma transformation for Time (add epsilon to avoid true zero)
df_on$Time_Avg_s_gamma <- df_on$Time_Avg_s + 0.000001

cat(">>> R: Fitting GLMMs (Beta & Gamma Families). This might take time...\n")

# --- GLMM MODELING ---

# 1. Model for F1-Score (Interaction: Algorithm * Window_Sec)
model_F1_on <- glmmTMB(
  F1_beta ~ Algorithm * Window_Sec + (1 | Database/Participant),
  data = df_on,
  family = beta_family(link = "logit")
)

# 2. Model for Jitter F1
model_JF_on <- glmmTMB(
  Jitter_F1_beta ~ Algorithm * Window_Sec + (1 | Database/Participant),
  data = df_on,
  family = beta_family(link = "logit")
)

# 3. Model for Computational Time (Gamma distribution)
model_CPU_on <- glmmTMB(
  Time_Avg_s_gamma ~ Algorithm * Window_Sec + (1 | Database/Participant),
  data = df_on,
  family = Gamma(link = "log")
)

# --- FIT QUALITY METRICS ---
cat("--- Fit Quality ---\n")
r2_f1 <- r2(model_F1_on); cat(sprintf("F1: Cond R2=%.3f\n", r2_f1$R2_conditional))
r2_jf <- r2(model_JF_on); cat(sprintf("JF: Cond R2=%.3f\n", r2_jf$R2_conditional))
r2_cpu <- r2(model_CPU_on); cat(sprintf("CPU: Cond R2=%.3f\n", r2_cpu$R2_conditional))

# --- POST-HOC ANALYSIS ---
cat(">>> R: Computing EMMs and Contrasts...\n")

# EMMs
emm_F1_on <- emmeans(model_F1_on, ~ Algorithm | Window_Sec, type = "response")
emm_JF_on <- emmeans(model_JF_on, ~ Algorithm | Window_Sec, type = "response")
emm_CPU_on <- emmeans(model_CPU_on, ~ Algorithm | Window_Sec, type = "response")

# Pairwise comparisons: Algorithms within each Window_Sec
posthoc_F1_on <- emmeans(model_F1_on, pairwise ~ Algorithm | Window_Sec, type = "response")
posthoc_JF_on <- emmeans(model_JF_on, pairwise ~ Algorithm | Window_Sec, type = "response")
posthoc_CPU_on <- emmeans(model_CPU_on, pairwise ~ Algorithm | Window_Sec, type = "response")

# Pairwise comparisons: Window_Sec within each Algorithm
posthoc_F1_on_WL <- emmeans(model_F1_on, pairwise ~ Window_Sec | Algorithm, type = "response")
posthoc_JF_on_WL <- emmeans(model_JF_on, pairwise ~ Window_Sec | Algorithm, type = "response")
posthoc_CPU_on_WL <- emmeans(model_CPU_on, pairwise ~ Window_Sec | Algorithm, type = "response")

# --- EXPORT TO EXCEL ---
cat(">>> R: Saving results to", output_file, "\n")
wb_on <- createWorkbook()

# EMM Sheets
addWorksheet(wb_on, "EMM_F1"); writeData(wb_on, "EMM_F1", as.data.frame(emm_F1_on))
addWorksheet(wb_on, "EMM_Jitter_F1"); writeData(wb_on, "EMM_Jitter_F1", as.data.frame(emm_JF_on))
addWorksheet(wb_on, "EMM_Time"); writeData(wb_on, "EMM_Time", as.data.frame(emm_CPU_on))

# Post-Hoc: Algorithm Comparisons
addWorksheet(wb_on, "PH_F1_Algo"); writeData(wb_on, "PH_F1_Algo", as.data.frame(posthoc_F1_on$contrasts))
addWorksheet(wb_on, "PH_JF_Algo"); writeData(wb_on, "PH_JF_Algo", as.data.frame(posthoc_JF_on$contrasts))
addWorksheet(wb_on, "PH_Time_Algo"); writeData(wb_on, "PH_Time_Algo", as.data.frame(posthoc_CPU_on$contrasts))

# Post-Hoc: Window Size Comparisons
addWorksheet(wb_on, "PH_F1_Win"); writeData(wb_on, "PH_F1_Win", as.data.frame(posthoc_F1_on_WL$contrasts))
addWorksheet(wb_on, "PH_JF_Win"); writeData(wb_on, "PH_JF_Win", as.data.frame(posthoc_JF_on_WL$contrasts))
addWorksheet(wb_on, "PH_Time_Win"); writeData(wb_on, "PH_Time_Win", as.data.frame(posthoc_CPU_on_WL$contrasts))

saveWorkbook(wb_on, output_file, overwrite = TRUE)
cat(">>> R: Online Analysis Complete.\n")