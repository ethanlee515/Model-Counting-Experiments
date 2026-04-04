.SECONDARY:

%.v:
	./mill Rtl.runMain $*

%.aag: %.v
	yosys --commands "\
	  read_verilog $<; \
	  prep -top $*; \
	  aigmap; \
	  write_aiger -ascii $@"

%.cnf: %.aag
	aigtocnf -m $*.aag $*.cnf

clean:
	rm -f *.v *.aag *.cnf
