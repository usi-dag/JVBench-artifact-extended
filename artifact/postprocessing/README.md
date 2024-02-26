# Generate Figures

To generate the figures, you can run:

```
python3.9 main.py
```

This command will produce PDF figures using the data in the `./data` directory.
The figures will be saved in the `./out` directory.

You can modify the input/output directories and other parameters using the optional arguments listed by the following command:

```
python3.9 main.py --help
```

Please note that figures may be suboptimal.
For instance, legends may overlap numbers.
Fine-tuning based on the output numbers is required to generate optimal figures.
