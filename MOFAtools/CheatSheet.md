# MOFAmodel object
MOFAmodel it is the main S4 class used to store all relevant data to analyse a MOFA model. Its slots are the following (accessible using @ or the correspon):
* **InputData**: input data, either a list of matrices or a MultiAssayExperiment
* **TrainData**: training data, a list of matrices with processed data (centered, scaled, etc.)
* **TrainOptions**: training options
* **DataOptions**: data processing options
* **ModelOptions**: model options
* **TrainStats**: training statistics
* **Expectations**: expectations of the different random variables
* **Status**: trained/untrained
* **Dimensions**: Number of views (M), samples (N), features per view (D) and factors (K)
* **ImputedData**: imputed data (filled by running imputeMissing on the object)


# List of relevant functions

## Prepare and run MOFA
* **createMOFAobject**: first function to create an untrained MOFA model from input multi-omics data  
* **prepareMOFA**: prepare an untrained MOFA, always run it after createMOFAobject and before runMOFA  
* **runMOFA**: function to train an untrained MOFA model. This calls the Python framework  
* **loadModel**: load a trained MOFA model from an hdf5 file stored in disk  

## get functions
* **factorNames**: get or set factor names  
* **featureNames**: get or set feature names  
* **sampleNames**: get or set sample names  
* **viewNames**: get or set view names  
* **getDimensions**: get dimensions (number of samples, features, etc.)  
* **getFactors**: get model factors  
* **getWeights**: get model weights  
* **getTrainData**: get training data  
* **getImputedData**: get imputed data  

## Disentangle sources of variation
* **plotVarianceExplained**: plot the variance explained by each factor in each view. This is the key plot of MOFA and should always be done before inspecting factors or weights.
* **calculateVarianceExplained**: calculate and return the variance explained by each factor in each view.

## Inspect loadings
* **plotTopWeights**: plot the top loadings for a given factor and view  
* **plotWeights**: plot all loadings for a given factor and view  
* **plotWeightsHeatmap**: plot a heatmap of the loadings from multiple factors in a given view

## Inspect factors
* **plotFactorCor**: correlation plot between factors. Ideally, they should be uncorrelated  
* **plotFactorScatter**: scatterplot between two factors, this is similar to doing a PCA plot  
* **plotFactorScatters**: pairwise combination of scatterplots between multiple factors  
* **plotFactorBeeswarm**: beeswarm plot for a single factor  

## Inspect the data
* **plotTilesData**: plot overview of the input data, including the number of samples, views, features, and the missing assays.
* **plotDataHeatmap**: heatmap of the training data using only top features for a given factor. This is very useful to map the factors and features back to the original data  
* **plotDataScatter**: scatterplot of the data using only top features for a given factor  

## Feature set enrichment analysis
* **runEnrichmentAnalysis**: do feature set enrichment analysis. Takes a bit amount of options, check the example on the vignette
* **plotEnrichment**: plot the top most enriched feature sets per factor
* **plotEnrichmentBars**: plot the number of enriched feature sets per factor as a barplot

## Clustering
* **clusterSamples**: k-means clustering of samples on the factor space

## Compare and select models
* **compareModels**: compare MOFAmodel objects from multiple runs in terms of number of factors and ELBO statistics (for model selection)
* **compareFactors**: compare MOFAmodel objects from multiple runs in terms of their factors
* **selectModel**: select the best MOFAmodel object from multiple MOFAmodel objects based on the ELBO

## Predictions and imputation
* **prediction**: predict observations
* **imputeMissing**: impute missing data

## Subset
* **subsetSamples**: subset samples
* **subsetViews**:  subset views
* **subsetFactors**: subset factors

## Examples
* **makeExampleData**: make example MOFAmodel object with simulated data



