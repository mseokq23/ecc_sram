`timescale 1ns/1ps
// ro_div: three rings with different periods, one enabled at a time (the others stand at 1).
// For each enable: DIV starts at 1 after reset, its period is 256 periods of that ring, the stopped taps
// do not count; with no enable DIV stays 1 even if a tap moves (the divider is held reset).
module tb;
    reg  [2:0] EN = 3'b000;
    reg  [2:0] TAP = 3'b111;
    reg  [2:0] glitch = 3'b000;
    wire DIV;
    ro_div dut (.TAP(TAP), .EN(EN), .DIV(DIV));

    real half [0:2];
    initial begin half[0] = 3.10; half[1] = 3.70; half[2] = 4.30; end
    always begin #(half[0]) TAP[0] = (EN[0] | glitch[0]) ? ~TAP[0] : 1'b1; end
    always begin #(half[1]) TAP[1] = (EN[1] | glitch[1]) ? ~TAP[1] : 1'b1; end
    always begin #(half[2]) TAP[2] = (EN[2] | glitch[2]) ? ~TAP[2] : 1'b1; end

    integer n_edges = 0, errors = 0, checks = 0, k;
    real t_first, t_last, per, expect;
    reg counting = 1'b0;
    always @(posedge DIV) if (counting) begin
        if (n_edges == 0) t_first = $realtime;
        t_last = $realtime; n_edges = n_edges + 1;
    end

    initial begin
        #20;
        checks = checks + 1;
        if (DIV !== 1'b1) begin errors = errors + 1; $display("reset: DIV=%b", DIV); end
        // a moving tap without an enable: divider held reset
        glitch = 3'b010; n_edges = 0; counting = 1'b1;
        #(3 * 256 * 7.4);
        counting = 1'b0; glitch = 3'b000;
        checks = checks + 1;
        if (n_edges != 0 || DIV !== 1'b1) begin errors = errors + 1; $display("no enable: %0d edges, DIV=%b", n_edges, DIV); end
        for (k = 0; k < 3; k = k + 1) begin
            EN = 3'b001 << k; n_edges = 0; counting = 1'b1;
            per = 2.0 * half[k];
            #(3.2 * 256 * per);
            counting = 1'b0;
            expect = 256.0 * per;
            checks = checks + 1;
            if (n_edges < 3 || ((t_last - t_first) / (n_edges - 1) - expect) > 0.05 || (expect - (t_last - t_first) / (n_edges - 1)) > 0.05) begin
                errors = errors + 1;
                $display("ring %0d: %0d edges, period %f ns, expected %f ns", k, n_edges, (t_last - t_first) / (n_edges - 1), expect);
            end else
                $display("ring %0d: DIV period %.2f ns = 256 x %.2f ns", k, (t_last - t_first) / (n_edges - 1), per);
            EN = 3'b000; #10;
            checks = checks + 1;
            if (DIV !== 1'b1) begin errors = errors + 1; $display("after ring %0d: DIV=%b (not reset)", k, DIV); end
        end
        $display("checks=%0d errors=%0d", checks, errors);
        if (errors == 0) $display("TB RESULT: PASS"); else $display("TB RESULT: FAIL");
        $finish;
    end
endmodule
