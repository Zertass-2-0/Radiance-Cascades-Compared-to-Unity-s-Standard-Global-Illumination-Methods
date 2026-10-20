# Radiance Cascades vs. Unity's Global Illumination Methods

**Experimental data and visual comparisons for research in Unity's Universal Render Pipeline (URP).**

This repository accompanies the DiGRA research project:

> **Comparative Evaluation of Real-Time Global Illumination Methods in Unity URP**

The study compares **Radiance Cascades** with Unity's standard global illumination (GI) methods, considering rendering performance and the visual characteristics of the resulting illumination. This repository makes the supporting measurements, figures, and comparison footage available for inspection.

## Repository Contents

| Resource | Description |
| --- | --- |
| [Measured Data](./Measured%20Data/) | Experimental measurements, including FPS and frame-time data, and figures used in the paper. |
| [Visual comparison videos](https://www.youtube.com/watch?v=daDjPJyB86o&list=PLaHv1eGKS6CyZF2IG05RV7KAHvvU5-xIQ) | YouTube playlist with recorded renders for qualitative comparison. |
| [LICENSE](./LICENSE) | MIT license for the repository. |

## Experimental Environment

| Component | Configuration |
| --- | --- |
| Game engine | Unity **6000.2.12f1** |
| Render pipeline | **Universal Render Pipeline (URP)** |
| GPU | **NVIDIA GeForce RTX 4060 Laptop GPU** |
| CPU | **Intel Core i7-13620H** |

## Evaluation

The materials support comparison along two dimensions:

- **Rendering performance:** Frames per second (**FPS**) and frame time (**ms**) characterize the runtime cost of each tested lighting approach. Higher FPS and lower frame time generally indicate faster rendering under comparable conditions.
- **Visual output:** Recorded renders provide a qualitative reference for the appearance of indirect illumination and other visible lighting differences.

To explore the results, review the files in [Measured Data](./Measured%20Data/), compare the reported measurements and figures with the paper, and watch the [video comparison playlist](https://www.youtube.com/watch?v=daDjPJyB86o&list=PLaHv1eGKS6CyZF2IG05RV7KAHvvU5-xIQ).

## Reproducibility and Scope

This is a **research-artifacts repository**, rather than a ready-to-run Unity project. The shared data support examination of the experiment, but reproducing its measurements also requires the scene assets, rendering configurations, and measurement procedure described in the study.

Results are specific to the experimental environment. Performance may differ with scene complexity, render resolution, quality settings, GPU drivers, and hardware.

## Research Paper and Citation

**Paper:** *Comparative Evaluation of Real-Time Global Illumination Methods in Unity URP*

If you use these materials in academic work, please cite the associated paper. Full bibliographic information can be added here when available.

## License

This repository is licensed under the **MIT License**. See [LICENSE](./LICENSE) for details.