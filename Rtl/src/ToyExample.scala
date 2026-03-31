import spinal.core._
import spinal.lib._

class ToyExample(grid_width: Int, error_count: Int) extends Component {
  val physical_errors = in port Vec.fill(grid_width, grid_width)(Bool())
  val transversals = Vec.fill(grid_width)(Bool())
  for(i <- 0 until grid_width) {
    transversals(i) := physical_errors(i).reduceBalancedTree(_ ^ _)
  }
  val s = transversals.sCount(True)
  val is_logical_error = (s >= (grid_width / 2) + 1)
  val flat_physical_errors = Vec(Bool(), grid_width * grid_width)
  for(i <- 0 until grid_width;
      j <- 0 until grid_width) {
    flat_physical_errors(i * grid_width + j) := physical_errors(i)(j)
  }
  val physical_errors_hamming = flat_physical_errors.sCount(True)
  val error_count_correct = (physical_errors_hamming === U(error_count))
  val add_to_count = out port Bool()
  add_to_count := is_logical_error & error_count_correct
}

object ToyVerilog extends App {
  SpinalVerilog(new ToyExample(5, 3))
}
