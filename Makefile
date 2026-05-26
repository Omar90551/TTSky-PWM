PROJ = tt_um_PWM
FILES = ./src/pwm_counter.v ./src/pwm_comparator.v ./src/tt_um_PWM.v
FREQ = 20
DIR = ./test/fpga/$(PROJ)/

.PHONY: prog_fpga all clean

all: prog_fpga

# Ensure output directory exists
$(DIR):
	mkdir -p $(DIR)

# RTL synthesis (Yosys)
$(DIR)$(PROJ).json: $(FILES) | $(DIR)
	yosys -l $(DIR)yosys.log \
	-p "synth_ice40 -top $(PROJ) -json $(DIR)$(PROJ).json" \
	$(FILES)

# Place and Route (nextpnr)
$(DIR)$(PROJ).asc: $(DIR)$(PROJ).json
	nextpnr-ice40 -l $(DIR)nextpnrPnR.log \
	--seed 1 \
	--freq $(FREQ) \
	--package sg48 \
	--up5k \
	--pcf ./test/fpga/icebreaker.pcf \
	--json $(DIR)$(PROJ).json \
	--asc $(DIR)$(PROJ).asc

# Bitstream generation (icepack)
$(DIR)$(PROJ).bin: $(DIR)$(PROJ).asc
	icepack $(DIR)$(PROJ).asc $(DIR)$(PROJ).bin

# Program FPGA
prog_fpga: $(DIR)$(PROJ).bin
	iceprog $(DIR)$(PROJ).bin

# Optional cleanup
clean:
	rm -rf $(DIR)