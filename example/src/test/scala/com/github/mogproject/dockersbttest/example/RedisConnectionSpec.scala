package com.github.mogproject.dockersbttest.example

import org.specs2.mutable._
import com.redis.RedisClientPool

trait context extends BeforeAfter {
  lazy val clients = new RedisClientPool(host = "localhost", port = 6379, database = 0)

  val keys = (1 to 100).map { i => f"test-sbt-parallel-$i%03d" }

  // takes over 100 * 100 ms = 10 seconds
  def insertWithSleep(valueSuffix: String) = keys.foreach { key =>
    clients.withClient(_.set(key, s"${key}-${valueSuffix}"))
    Thread.sleep(100L)
  }

  def before = clear
  def after = clear
  def clear = keys.foreach { key => clients.withClient(_.del(key)) }
}

object RedisConnectionSpec1 extends Specification {
  "test1" should {
    "insert 100 records and delete 1 record" in new context {
      insertWithSleep("test1")
      clients.withClient(_.del("test-sbt-parallel-100"))
      clients.withClient(_.dbsize) must beSome(99L)
    }
  }
}

object RedisConnectionSpec2 extends Specification {
  "test2" should {
    "insert 100 records and delete 1 record" in new context {
      insertWithSleep("test2")
      clients.withClient(_.del("test-sbt-parallel-099"))
      clients.withClient(_.dbsize) must beSome(99L)
    }
  }
}

object RedisConnectionSpec3 extends Specification {
  "test3" should {
    "insert 100 records and delete 1 record" in new context {
      insertWithSleep("test3")
      clients.withClient(_.del("test-sbt-parallel-098"))
      clients.withClient(_.dbsize) must beSome(99L)
    }
  }
}

object RedisConnectionSpec4 extends Specification {
  "test4" should {
    "insert 100 records and delete 1 record" in new context {
      insertWithSleep("test4")
      clients.withClient(_.del("test-sbt-parallel-097"))
      clients.withClient(_.dbsize) must beSome(99L)
    }
  }
}
