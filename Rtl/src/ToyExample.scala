import spinal.core._
import spinal.lib._

class ToyExample(n: Int) extends Component {
  val physical_errors = in port Vec.fill(n, n)(Bool())
  val transversals = Vec.fill(n)(Bool())
  for(i <- 0 until n) {
    transversals(i) := physical_errors(i).reduceBalancedTree(_ ^ _)
  }
  val s = transversals.sCount(True)
  val logical_error = out port Bool()
  logical_error := (s >= (n / 2) + 1)
}

object ToyVerilog extends App {
  SpinalVerilog(new ToyExample(3))
}
