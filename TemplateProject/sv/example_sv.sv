module example_tb;

    example example_M(.*);

//_____________________________________________________________
//cnt_iteration_sv
    int cnt_iteration_sv = 0;
    initial begin
        forever begin 
            #10;
            cnt_iteration_sv++;
        end
    end
//_____________________________________________________________

    initial begin
        $shm_open("waves.shm"); 
        $shm_probe("ASM");
        // $sdf_annotate("./results/sdf/example.sdf",DUT,,,"MAXIMUM");
    end
endmodule