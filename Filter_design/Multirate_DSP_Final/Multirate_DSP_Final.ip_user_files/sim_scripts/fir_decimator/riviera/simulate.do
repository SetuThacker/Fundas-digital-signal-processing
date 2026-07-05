transcript off
onbreak {quit -force}
onerror {quit -force}
transcript on

asim +access +r +m+fir_decimator  -L xbip_utils_v3_0_10 -L axi_utils_v2_0_6 -L fir_compiler_v7_2_19 -L xil_defaultlib -L secureip -O5 xil_defaultlib.fir_decimator

do {fir_decimator.udo}

run 1000ns

endsim

quit -force
