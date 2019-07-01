package org.ieimlengine

// IMPORT NECESSARY PACKAGES
import org.apache.spark.sql.SparkSession
import net.liftweb.json._
import net.liftweb.json.DefaultFormats
import org.apache.spark.ml.clustering.KMeans
import org.apache.spark.ml.clustering.KMeansModel
import org.apache.spark.ml.feature.VectorAssembler
import java.util.Calendar
import java.io.FileNotFoundException
import scala.annotation.switch
import sys.process._
import org.apache.log4j.{Level, LogManager}

// A case class has to be defined with respective parameters for each algorithm
// Main object of this package

case class KM(mode: Option[Int],
              k: Option[Int],
              maxIter: Option[Int],
              featuresCol: Option[String],
              predictionCol: Option[String],
              seed: Option[Long],
              tol: Option[Double],
              initMode: Option[String],
              initSteps: Option[Int],
              feature_names: Option[Array[String]]) {
  def defaults = copy(
    mode = mode orElse Some(0),
    k = k orElse Some(2),
    maxIter = maxIter orElse Some(20),
    featuresCol = featuresCol orElse Some("features"),
    predictionCol = predictionCol orElse Some("prediction"),
    seed = seed orElse Some(-1689246527),
    tol = tol orElse Some(0.0001),
    initMode = initMode orElse Some("k-means||"),
    initSteps = initSteps orElse Some(2),
    feature_names = feature_names orElse Some(null)
  )
}

class Clustering(datafile:String, algid:Int, modelfile:String, algparams:String,outpath:String ) {

  // Json reading and extraction
  implicit val formats = DefaultFormats
  val json = algparams
  val hdfstohost = true
  (algid: @switch) match {
    case 21 => {
      val prms = parse(json).extract[KM].defaults

      if (prms.mode.get == 1 & modelfile == null) {
        throw new FileNotFoundException("Mode 1 requested but model file not found")
        sys.exit(-1)
      }

      println("STARTING SPARK SESSION")
      val spark = SparkSession
        .builder
        .appName(s"${this.getClass.getSimpleName}")
        .master("local[4]")
        .getOrCreate()

      LogManager.getRootLogger.setLevel(Level.INFO) //to print the logs info logs

      // Read csv file
      val read_data = spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load(datafile)

      // get input features as arrays and convert to features column
      val col_names = {
        if (prms.feature_names.get == null) {
          read_data.columns
        } else prms.feature_names.get
      }

      val assembler = new VectorAssembler()
        .setInputCols(col_names).setOutputCol(prms.featuresCol.get)

      val dataset = assembler.transform(read_data)
      println(s"Total number of datas: ${dataset.count()}") // count of data

      // The Schema will be printed to the USER
      println("DATAFRAME SCHEMA :")
      println(dataset.printSchema)

      val dt = Calendar.getInstance().getTime.toString.split("\\s+")(3).split(":")
      val time = dt.mkString(".")

      // Training - 80%, Testing - 20%
      val splits = dataset.randomSplit(Array(0.8, 0.2))
      val (trainingData, testData) = (splits(0), splits(1))

      // Running training Kmeans
      if (prms.mode.get == 0) {
       println("Requested KMeans Clustering Mode 0")

        // calling json elements as scala objects
        val kmeans = new KMeans()
          .setK(prms.k.get)
          .setMaxIter(prms.maxIter.get)
          .setFeaturesCol(prms.featuresCol.get)
          .setPredictionCol(prms.predictionCol.get)
          .setSeed(prms.seed.get)
          .setTol(prms.tol.get)
          .setInitMode(prms.initMode.get)
          .setInitSteps(prms.initSteps.get)

        val startTime = System.nanoTime()
        val kmModel = kmeans.fit(trainingData) // TRAINING
        val elapsedTime = (System.nanoTime() - startTime) / 1e9
        println(s"Training time: $elapsedTime seconds")

        // Evaluate clustering by computing Within Set Sum of Squared Errors.
        println("EVALUATING MODEL USING WSSSE")
        val WSSSE = kmModel.computeCost(trainingData)
        println(s"Within Set Sum of Squared Errors = $WSSSE")

        // Writing the model to the output path
        println(s"Writing the model file to $modelfile")
        kmModel.write.save(modelfile.concat(s"/km_model_$time"))

        /*
        Predicted data will be printed along with test data details, so test data is not saved separately
        */

        // Writing train data - Can be useful for user
        trainingData.select(col_names.head, col_names.tail:_*)
          .write.format("csv").option("header","true").option("multiline","true")
          .save(outpath.concat(s"/mode0_km_trainingData80_$time"))

        testData.select(col_names.head, col_names.tail:_*)
          .write.format("csv").option("header","true")
          .save(outpath.concat(s"/mode0_km_testData20_$time"))

        println("Predicting Test data obtained from 20% of given input")
        val predict0 = kmModel.transform(testData)
        val cols = predict0.drop(prms.featuresCol.get).columns
        println(s"Writing the predicted dataframe to $outpath")

        predict0.select("prediction","petalwidth","petallength")
          .write.format("csv").option("header","true")
          .save(outpath.concat(s"/mode0_km_predicted_$time"))
        kmModel.clusterCenters.foreach(println)

//        predict0.select(cols.head, cols.tail: _*)
//          .write.format("csv").option("header","true")
//          .save(outpath.concat(s"/mode0_km_predicted_$time"))
//
        //The below if statement is used to retrieve files from hdfs to host

        if (hdfstohost==true) {
          val result = "hdfs dfs -get " + s"$modelfile" + s"/km_model_$time" + " /tmp/data" !
          val train80 = "hdfs dfs -get " + s"$outpath" + s"/mode0_km_trainingData80_$time" + " /tmp/data"!
          val test20 = "hdfs dfs -get " + s"$outpath" + s"/mode0_km_testData20_$time" + " /tmp/data"!
          val result_print = "hdfs dfs -get " + s"$outpath" + s"/mode0_km_predicted_$time" + " /tmp/data"!
        }

      }
      if (prms.mode.get == 1) {
        val model = KMeansModel.load(modelfile)
        println("PREDICTION STARTED")
        val predict1 = model.transform(dataset)
        println(predict1.printSchema)
        predict1.show() // show top 20 rows
        val cols = predict1.drop(prms.featuresCol.get).columns
        predict1.select("prediction","petalwidth","petallength")
          .write.format("csv").option("header","true")
          .save(outpath.concat(s"/mode1_km_predicted_$time"))

//        predict1.select(cols.head, cols.tail: _*)
//          .write.format("csv").option("header","true")
//          .save(outpath.concat(s"/mode1_km_predicted_$time"))

        if (hdfstohost==true) {
          val result_pred = "hdfs dfs -get " + s"$outpath" + s"/mode1_km_predicted_$time" + " /tmp/data" !
        }
      }
      spark.stop()
    }
  }
}
