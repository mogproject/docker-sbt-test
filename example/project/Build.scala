import sbt._
import sbt.Keys._

object ApplicationBuild extends Build {

  val appName = "test-sbt-parallel"
  val appVersion = "0.1.0-SNAPSHOT"
  val appScalaVersion = "2.10.3"

  val appScalaOptions = Seq(
    "-deprecation",
    "-unchecked",
    "-feature",
    // "-optimize",
    "-encoding", "utf-8"
  )

  val appResolvers = Seq(
    "Sonatype OSS Releases" at "http://oss.sonatype.org/content/repositories/releases",
    "Sonatype OSS Snapshots" at "http://oss.sonatype.org/content/repositories/snapshots",
    "Typesafe Repository" at "http://repo.typesafe.com/typesafe/releases/"
  )

  val appDependencies = Seq(
    "org.scalatest" %% "scalatest" % "1.9.1" % "test",
    "org.specs2" %% "specs2" % "1.13" % "test",
    "net.debasishg" % "redisclient_2.10" % "2.11"
  )

  lazy val main = Project(
    id = appName.toLowerCase,
    base = file(".")
  ).settings(
    name := appName,
    version := appVersion,
    scalaVersion := appScalaVersion,
    scalacOptions ++= appScalaOptions,
    resolvers ++= appResolvers,
    libraryDependencies ++= appDependencies,
    parallelExecution in Test := false
  )

}
