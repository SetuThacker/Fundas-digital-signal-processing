`timescale 1ns / 1ps

module multirate_system(
    input wire clk,
    input wire reset,
    
    // Input from the Testbench (120 MHz)
    input wire [15:0] s_axis_input_tdata,
    input wire        s_axis_input_tvalid,
    
    // Output to the Testbench (480 MHz effective rate, parallelized)
    output wire [63:0] m_axis_output_tdata,
    output wire        m_axis_output_tvalid,
    
    // Exposing the decimated signal for analysis (40 MHz effective rate)
    output wire [15:0] probe_decimated_tdata,
    output wire        probe_decimated_tvalid
);

    // Internal wires to connect the Decimator to the Interpolator
    wire [15:0] internal_tdata;
    wire        internal_tvalid;

    // Output assignment for the probe (so we can save it to a file later)
    assign probe_decimated_tdata = internal_tdata;
    assign probe_decimated_tvalid = internal_tvalid;

    // -------------------------------------------------------------------------
    // Instantiate the Decimator IP (Decimate by 3)
    // -------------------------------------------------------------------------
    fir_decimator decimator_inst (
        .aclk               (clk),
        .s_axis_data_tvalid (s_axis_input_tvalid),
        .s_axis_data_tready (), // Ignoring ready signal for simplicity in simulation
        .s_axis_data_tdata  (s_axis_input_tdata),
        
        .m_axis_data_tvalid (internal_tvalid),
        .m_axis_data_tdata  (internal_tdata)
    );

    // -------------------------------------------------------------------------
    // Instantiate the Interpolator IP (Interpolate by 12)
    // -------------------------------------------------------------------------
    // Note: The input to this module is the output of the decimator.
    // The output is 64-bits wide because 480 MHz / 120 MHz clock = 4 parallel samples.
    // (4 samples * 16 bits/sample = 64 bits)
    fir_interpolator interpolator_inst (
        .aclk               (clk),
        .s_axis_data_tvalid (internal_tvalid),
        .s_axis_data_tready (), 
        .s_axis_data_tdata  (internal_tdata),
        
        .m_axis_data_tvalid (m_axis_output_tvalid),
        .m_axis_data_tdata  (m_axis_output_tdata)
    );

endmodule