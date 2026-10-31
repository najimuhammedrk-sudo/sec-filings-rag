import os
import matplotlib.pyplot as plt

os.makedirs("docs", exist_ok=True)
BLUE, GREY, RED = "#1f4e79", "#9aa5b1", "#b23a48"

# Chart 1: retrieval hit@5 by routing mode (fixed chunks, n=11)
labels = ["Hand-filtered\n(upper bound)", "Routed +\nlatest default", "Routed,\nno default", "Unfiltered"]
vals = [9, 8, 6, 3]
fig, ax = plt.subplots(figsize=(8, 4.5))
bars = ax.bar(labels, vals, color=[GREY, BLUE, BLUE, RED])
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.2, f"{v}/11", ha="center", fontweight="bold")
ax.set_ylim(0, 11)
ax.set_ylabel("Questions with evidence in top 5")
ax.set_title("Retrieval hit@5 by routing mode (n = 11)")
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.01, "Small sample: one question = 9 points. Fixed 150-word chunks.", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("docs/retrieval_hit5.png", dpi=200)
plt.close(fig)

# Chart 2: wrongly refused answerable questions, by run
runs = ["R6\n2/11", "R7\n2/11", "R8\n1/11", "R9\n2/11", "R10\n1/11", "R11\n1/19", "R12\n1/19"]
pct = [18.2, 18.2, 9.1, 18.2, 9.1, 5.3, 5.3]
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(runs, pct, marker="o", color=BLUE, linewidth=2)
for x, y in zip(runs, pct):
    ax.text(x, y + 1, f"{y:.0f}%", ha="center", fontsize=9)
ax.axvline(4.5, color=GREY, linestyle="--")
ax.text(4.55, 22, "question set grew\n11 to 19", fontsize=8, color="gray")
ax.set_ylim(0, 25)
ax.set_ylabel("% of answerable questions refused")
ax.set_title("Wrongly refused answerable questions, by run")
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.01, "Not a clean trend: the denominator changed at R11.", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("docs/wrongly_refused.png", dpi=200)
plt.close(fig)

# Chart 3: unanswerable questions correctly refused
fig, ax = plt.subplots(figsize=(8, 4.5))
runs3 = ["R6", "R7-R12"]
ok = [4, 10]
tot = [4, 10]
ax.bar(runs3, ok, color=BLUE)
for i, (o, t) in enumerate(zip(ok, tot)):
    ax.text(i, o + 0.2, f"{o}/{t}", ha="center", fontweight="bold")
ax.set_ylim(0, 12)
ax.set_ylabel("Unanswerable questions refused")
ax.set_title("Hallucination guard: unanswerable questions refused (n = 10)")
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.01, "Graded by eye; the refusal prompt was tuned on this same set.", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("docs/unanswerable_refused.png", dpi=200)
plt.close(fig)
print("saved to docs/")