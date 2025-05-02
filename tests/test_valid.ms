<!- Comprehensive Test File for MiniSoft Compiler -!>
MainPrgm FullTestProgrm;

Var
    {-- === Variable Declarations === --}
    <!- Simple Integer Variables -!>
    let counter, index, temp_val : Int;
    let result_flag : Int; 
    let count, limit, i : Int;

    <!- Simple Float Variables -!>
    let average, sum, tolerance : Float;
    let ratio, total : Float;

    <!- Multiple variables declared together -!>
    let loop_var1, loop_var2, step_val : Int;
    let f1, f2, f3 : Float;

    <!- Integer Array -!>
    let data_array : [Int; 20];
    let names : [Int; 5];

    <!- Float Array -!>
    let readings : [Float; 10];
    let flags : [Float; 10];

    <!- Variables for Input -!>
    let user_int : Int;
    let user_float : Float;
    let user_choice : Int;

    {-- === Constant Declarations === --}
    @define Const MAX_SIZE : Int = 20;
    @define Const PI : Float = 3.14159;
    @define Const START_VALUE : Int = 1;
    @define Const THRESHOLD : Float = (+0.05); <!- Signed float constant -!>
    @define Const THRESHOLD2 : Float = (-0.05); <!- Signed float constant -!>
    @define Const NEG_LIMIT : Int = (-10);     <!- Signed integer constant -!>
    @define Const MAX_ITER : Int = (+100);
    @define Const COMPANY_CODE : Int = 32767; <!- Max Int range -!>
    @define Const NEG_VAL : Int = (-50);


BeginPg
{
    {-- 
    === Initialization === 
    --}

    readings[9] := 55655554;
    readings[9] := 0;
    names[0] := 10;
    names[1] := names[0] + NEG_VAL;
    total := count;     <!- Valid: Assign Int to Float -!>
    counter :=  5555;
    index :=44;
    index := START_VALUE; <!- Using a constant -!>
    sum := 0.0;
    tolerance := THRESHOLD;
    step_val := (-5);
    result_flag := 50;
    limit := MAX_ITER;
    count := 500;
    total := 0.0;
    data_array[0] := NEG_LIMIT;
    readings[9] := PI * 2.0; <!- Expression in assignment -!>

    {--
        Multi-line comment example.
    --}

    {-- === Input Example === --}
    output("Enter an integer: ");
    input(user_int);
    input(ratio);
    output("Enter a float: ");
    input(user_float);
    output("You entered Int: ", user_int, " and Float: ", user_float);

    {-- === Simple Assignment and Expressions === --}
    temp_val := user_int * (5 + data_array[0]);
    average := (user_float + readings[9]) / 2.0;
    output("Calculated temp_val: ", temp_val, " average: ", average);

    result_flag := ( user_int+user_choice > 10 AND user_float == PI OR (user_int > 10 AND user_float < PI)); <!- Logical assignment (assuming 1/0 result) -!>
    output("Result flag (int > 10 AND float < PI): ", result_flag);

    {-- === Conditional Statements === --}
    if (user_int == COMPANY_CODE) then {
        output("User integer matches company code!");
    } else {
        output("User integer does NOT match company code.");
    }
    

    if (ratio > 0.0) then {
        output("Ratio is positive: ", ratio);
        if (ratio > 0.0) then {
        output("Ratio is positive: ", ratio);
        }
    } 
    else {
        output("Ratio is non-positive: ", ratio);
        if (ratio > 0.0) then {
            output("Ratio is positive: ", ratio);
            if (ratio > 0.0) then {
            output("Ratio is positive: ", ratio);
                if (ratio > 0.0) then {
                output("Ratio is positive: ", ratio);
                }
            } else {
                output("Ratio is non-positive: ", ratio);
                if (ratio > 0.0) then {
                output("Ratio is positive: ", ratio);
                }
            }
        }
    }

    {-- Example Loops --}

    do {
        total := total + (count * ratio);
        count := count + 1;
        output("Count:", count, " Total:", total);
    } while (count < limit);


    for i from 0 to 4 step 1 {
          names[i] := i * 10;
          output("names[", i, "] = ", names[i]);
    }

    {-- === Nested Loops Example 1: For-in-For === --}
    output("--- Nested For Loops ---");
    for loop_var1 from 1 to 3 step 1 {
        output("Outer loop 1: ", loop_var1);
        <!- Inner loop with potentially calculation-derived bounds/step -!>
        for loop_var2 from data_array[0] + 11 to MAX_SIZE step loop_var1 + 1 {
             output("  Inner loop 1: ", loop_var2);
        }
        {-- Comment inside loop block --}
    }

    {-- === Nested Loops Example 2: DoWhile-in-For === --}
    output("--- Nested DoWhile-in-For Loop ---");
    for loop_var1 from 0 to 1 step 1 {
         output("Outer loop 2: ", loop_var1);
         counter := 3; <!- Reset inner loop counter -!>
         do {
             output("  Inner loop 2 (DoWhile): ", counter);
             readings[counter] := loop_var1 * 1.5 + counter; <!- Update array -!>
             counter := counter - 1;
         } while (counter > 0);
    }

    {-- === Nested Loops Example 3: For-in-DoWhile === --}
    output("--- Nested For-in-DoWhile Loop ---");
    counter := 0;
    do {
         output("Outer loop 3 (DoWhile): ", counter);
         for index from 1 to 2 step 1 {
              output("  Inner loop 3 (For): ", index);
              if (index == 5) then {
                  output("    Index is one");
              } else {
                  output("    Index is not one");
              }
         }
         counter := counter + 1;
    } while (! counter < 2 AND readings[counter] < PI); <!- Complex while condition -!>


    {-- === Nested Loops Example 4: DoWhile-in-DoWhile === --}

    output("--- Nested DoWhile-in-DoWhile Loop ---");
    loop_var1 := 0;
    do {
        output("Outer loop 4 (DoWhile): ", loop_var1);
        loop_var2 := 2;
        do {
            output("  Inner loop 4 (DoWhile): ", loop_var2);
            temp_val := loop_var1 + loop_var2;
            output("    Temp sum: ", temp_val);
            loop_var2 := loop_var2 - 1;
        } while (loop_var2 >= 1);
        loop_var1 := loop_var1 + 1;
    } while (loop_var1 < 2);


    {-- === Using array elements and constants extensively === --}

    data_array[index] := (data_array[0] + MAX_SIZE) / 2;
    output("Data array element 5: ", data_array[index]);

    ; <!- Empty instruction -!>

    {-- Final Output --}
    output("--- End of Program ---");
    output("Final counter value: ", counter);
    output("Final average value: ", average);

}
EndPg;

<!- End of the MiniSoft test program -!>