// Placeholder module that proves the toolchain and CI work end to end.
// Delete once real RTL and tests exist.
module smoke #(
    parameter int W = 64
) (
    input  logic         clk,
    input  logic         rst,
    input  logic [W-1:0] d,
    output logic [W-1:0] q
);
    always_ff @(posedge clk) begin
        if (rst) q <= '0;
        else     q <= d;
    end
endmodule
