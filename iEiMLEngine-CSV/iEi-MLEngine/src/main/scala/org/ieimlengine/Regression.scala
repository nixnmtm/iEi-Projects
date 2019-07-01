package org.ieimlengine

/**
  * Created by nixon on 12/13/2017.
  */

// IMPORT NECESSARY PACKAGES
import org.apache.log4j.{Level, LogManager}
import org.apache.spark.sql.{DataFrame, SparkSession}
import net.liftweb.json._
import net.liftweb.json.DefaultFormats
import org.apache.spark.ml.regression.LinearRegression
import org.apache.spark.ml.regression.LinearRegressionModel
import org.apache.spark.ml.feature.VectorAssembler
import java.util.Calendar
import java.io.FileNotFoundException
import scala.annotation.switch
import scala.sys.process._


case class LR(mode: Option[Int],
              elasticNetParam: Option[Double],
              featuresCol: Option[String],
              solver: Option[String],
              fitIntercept: Option[Boolean],
              regParam: Option[Double],
              labelcol: Option[String],
              predictionCol: Option[String],
              maxIter: Option[Int],
              weightCol: Option[String], /// think about this
              standardization: Option[Boolean],
              tol: Option[Double],
              aggregationDepth: Option[Int],
              featureColnames: Option[Array[String]]) {
  def defaults = copy(
    mode = mode orElse Some(0),
    elasticNetParam = elasticNetParam orElse Some(0.0),
    featuresCol = featuresCol orElse Some("features"),
    solver = solver orElse Some("auto"),
    fitIntercept = fitIntercept orElse Some(true),
    regParam = regParam orElse Some(0.0),
    labelcol = labelcol orElse Some("label"),
    predictionCol = predictionCol orElse Some("prediction"),
    maxIter = maxIter orElse Some(100),
    standardization = standardization orElse Some(true),
    tol = tol orElse Some(1.0E-6),
    aggregationDepth = aggregationDepth orElse Some(2),
    featureColnames = featureColnames orElse Some(null)
  )
}

class Regression(datafile:String, algid:Int, modelfile:String, algparams:String,outpath:String ) {

  // Json reading and extraction
  implicit val formats = DefaultFormats

  val json = algparams
  val hdfstohost = true
  (algid: @switch) match {
    case 11 => {

      val prms = parse(json).extract[LR].defaults

      if (prms.mode.get == 1 & modelfile == null) {
        throw new FileNotFoundException("Mode 1 requested but model file not found")
        sys.exit(-1)
      }

      println("STARTING SPARK SESSION")
      val spark = SparkSession
        .builder
        .appName(s"${this.getClass.getSimpleName}")
        .master("local[2]")
        .getOrCreate()

      LogManager.getRootLogger.setLevel(Level.INFO) //to print the logs info logs

      // Read csv file
      val read_data = spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load(datafile)
      // get input features as arrays and convert to features column
      val col_names = {
        if (prms.featureColnames.get == null) {
          read_data.columns
        } else prms.featureColnames.get
      }

      val feature_cols = col_names.filter(!_.contains(prms.labelcol.get)) // dropping label column

      val add_featVec = new VectorAssembler()
        .setInputCols(feature_cols).setOutputCol(prms.featuresCol.get) // for CSV

      val dataset = add_featVec.transform(read_data)
      dataset.select(prms.labelcol.get).rdd.map(_.getDouble(0))
      println(s"Total number of datas: ${dataset.count()}") // count of data

      // The Schema will be printed to the USER
      println("DATAFRAME SCHEMA :")
      println(dataset.printSchema)

      val dt = Calendar.getInstance().getTime.toString.split("\\s+")(3).split(":")
      val time = dt.mkString(".")

      // Running training Linear Regression
      if (prms.mode.get == 0) {
        println("Requested LinerRegression Mode 0")

        // calling json elements as scala objects
        val lr = new LinearRegression()
          .setElasticNetParam(prms.elasticNetParam.get)
          .setMaxIter(prms.maxIter.get)
          .setFeaturesCol(prms.featuresCol.get)
          .setTol(prms.tol.get)
          .setFitIntercept(prms.fitIntercept.get)
          .setRegParam(prms.regParam.get)
          .setSolver(prms.solver.get)
          .setStandardization(prms.standardization.get)
          .setLabelCol(prms.labelcol.get)
          .setPredictionCol(prms.predictionCol.get)
          .setAggregationDepth(prms.aggregationDepth.get)

        // Training - 80%, Testing - 20%
        val splits: Array[DataFrame] = dataset.randomSplit(Array(0.8, 0.2), seed = 12345)

        val trainingData = splits(0).cache()
        val testData = splits(1).cache()
        val startTime = System.nanoTime()
        val lrModel = lr.fit(trainingData) // TRAINING
        val elapsedTime = (System.nanoTime() - startTime) / 1e9
        println(s"Training time: $elapsedTime seconds")

        // Writing the model to the output path
        println(s"Writing the model file to $modelfile")
        lrModel.write.save(modelfile.concat(s"/lr_model_$time"))

        /*
        Predicted data will also have the test data details printed
        */
        // Writing train data
        trainingData.select(col_names.head, col_names.tail:_*)
          .write.format("csv").option("header","true")
          .save(outpath.concat(s"/mode0_lr_trainingData80_$time"))
        testData.select(col_names.head, col_names.tail:_*)
          .write.format("csv").option("header","true")
          .save(outpath.concat(s"/mode0_lr_testData20_$time"))


        // Summarize the model over the training set and print out some metrics
        val trainingSummary = lrModel.summary
        println(s"numIterations: ${trainingSummary.totalIterations}")
        println(s"objectiveHistory: [${trainingSummary.objectiveHistory.mkString(",")}]")
        println(s"RMSE: ${trainingSummary.rootMeanSquaredError}")
        println(s"r2: ${trainingSummary.r2}")

        // Save the residuals
        trainingSummary.residuals.select("residuals")
          .write.format("csv").option("header","true")
          .save(outpath.concat(s"/mode0_lr_residuals_$time"))


        // Print the weights and intercept for linear regression.
        println(s"Weights:\n ${lrModel.coefficients} \nIntercept:\n ${lrModel.intercept}")

        val fullPredictions = lrModel.transform(testData).cache()
        val cols = fullPredictions.drop(prms.featuresCol.get).columns

        // Save the Full Predictions dataframe
        fullPredictions.select(cols.head, cols.tail: _*)
          .write.format("csv").option("header","true")
          .save(outpath.concat(s"/mode0_lr_predicted_$time"))


        println(s"Trained Data Size: ${trainingData.count()}")
        println(s"Predicted Data Size: ${fullPredictions.count()}")
        println(s"Test Data Size: ${testData.count()}")

        if (hdfstohost==true){
          val result_model = "hdfs dfs -get " + s"$modelfile" + s"/lr_model_$time" + " /tmp/data"!
          val train80 = "hdfs dfs -get " + s"$outpath" + s"/mode0_lr_trainingData80_$time" + " /tmp/data"!
          val test20 = "hdfs dfs -get " + s"$outpath" + s"/mode0_lr_testData20_$time" + " /tmp/data"!
          val result_pred20 = "hdfs dfs -get " + s"$outpath" + s"/mode0_lr_predicted_$time" + " /tmp/data"!
          val result_residue = "hdfs dfs -get " + s"$outpath" + s"/mode0_lr_residuals_$time" + " /tmp/data"!
        }

      }

      if (prms.mode.get == 1) {
        val model = LinearRegressionModel.load(modelfile)
        println("PREDICTION STARTED")
        val predict1 = model.transform(dataset)
        println(predict1.printSchema)
        predict1.show() // show top 20 rows
        val cols = predict1.drop(prms.featuresCol.get).columns
        predict1.select(cols.head, cols.tail: _*)
          .write.format("csv").option("header","true")
          .save(outpath.concat(s"/mode1_lr_predicted_$time"))
        if (hdfstohost==true) {
          val result_pred = "hdfs dfs -get " + s"$outpath" + s"/mode1_lr_predicted_$time" + " /tmp/data" !
        }
      }
      spark.stop()
    }
  }
}
