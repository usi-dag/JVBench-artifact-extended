import subprocess

# List of scripts to be called in order
scripts = [
    "ratios.py",
    "execution_overheads.py",
    "compile_time.py",
    "memory.py",
    "memory_pattern_benchmarks.py",
    "plot_ratios.py",
    "plot_memory_overhead.py",
    "plot_memory_overhead_pattern.py",
    "plot_speedup_factor.py",
    "plot_compilation_overhead.py",
    
]

# Execute each script in order
for script in scripts:
    print("\n" + "="*80 + "\n")
    print(f"Executing {script}")
    subprocess.run(["python3", script])
