package org.ieimlengine

/**
  * Created by nixon on 12/19/2017.
  *
  * This Scala Program gets data input, output path and parameters (json) from user
  * and executes Clustering based on the estimator requested.
  *
  * Usage: Clustering [options]
  * -p, --parentid <value>   Algorithm parent
  * -a, --algoid <value>     Algorithm estimator id
  * -f, --infile <value>     Input file with path
  * -p, --algparams <value>   Input parameters in json format
  * -m, --modelfile <value>  Model file with full path, required for mode 1
  * -o, --output <value>     output path
  *
  * The estimator parameters are given through commandline flag --inparams or -i in json format.
  * The json format has two required keys named algo_id(Estimator) and mode and others are optional.
  * If other parameters are not mentioned, the estimator will be executed with default values.
  *
  * Users can also choose the features to include in the run. If not, all the features are included.
  *
  * Based on the mode requested (default=0)
  *   Mode 0 : (i) Executes the training and prediction by splitting input dataset in 80:20 ratio
  *            (ii) Trains from 80% of given dataset and saves the model in the given output path
  *            (iii) Predicts the 20% and saves the prediction as csv file
  *
  *   Mode 1 : (i) Gets model file from user and executes prediction.
  *            (ii) Saves the prediction to output path
  *
  *In both the modes, the input file (-i or --infile) can be used to source the data(mode 0) and test data (mode 1)
  */


import scopt.OptionParser

case class globalparams(parentid: Int = 2,
                        algoid: Int = 21,
                        infile: String = null,
                        algparams: String = null,
                        modelfile: String = null,
                        output: String = null)
object mlengine extends App {
 // def main(args: Array[String]) {
    // Command Line argument Parsing
    val parser = new OptionParser[globalparams]("mlengine") {
      head("iEi MLEngine", "1.0")
      //head("iEi MLEngine")

   opt[Int]('d', "parentid")
        .required()
        .text(s"Parent Algorithm to use")
        .action { (x, c) => c.copy(parentid = x) }
      opt[Int]('a', "algoid")
        .required()
        .text(s"Algorithm id to use")
        .action { (x, c) => c.copy(algoid = x) }
      opt[String]('f', "infile")
        .required()
        .action { (x, c) => c.copy(infile = x) }
        .text("Input file with path")
      opt[String]('p', "algparams")
        .required()
        .action { (x, c) => c.copy(algparams = x) }
        .text("Input parameters in json format")
      opt[String]('o', "output")
        .required()
        .action { (x, c) => c.copy(output = x) }
        .text("output path")
      opt[String]('m', "modelfile")
        .action { (x, c) => c.copy(modelfile = x) }
        .text("Model file with full path, required for mode 1")
    }

    parser.parse(args, globalparams()) foreach { gparams =>
      val p = (gparams.infile, gparams.algoid, gparams.modelfile, gparams.algparams, gparams.output)

      if (gparams.parentid == 1) {
        val reg = new Regression(p._1,p._2,p._3,p._4,p._5)
      }
      if (gparams.parentid == 2) {
        val clus = new Clustering(p._1,p._2,p._3,p._4,p._5)
        clus.
      }
    }
 // }
}
