MainPrgm TestProwqedqwqwdewdqwdqegram1; <!- Error: exceeds maximum length of 14 characters -!>

Var
    let count, limit, i : Int;
    let total,totals : Float;

    let names : [Int; 5];
    let int_array : [Int; 10];

    let float_array : [Float; 10];
    let flags : [Float; 10];

    @define Const MAX_ITER : Int = 100;
    @define Const BAD_RANGE1 : Int = 40000; <!- Error: Out of range -!>
    @define Const BAD_RANGE2 : Int = (+40000); <!- Error: Out of range -!>
    @define Const BAD_RANGE3 : Int = (-40000); <!- Error: Out of range -!>

    @define Const TYPE_ERR : Int = 3.5;  <!- Error: Type mismatch -!>

    let count,limit : Float;              <!- Error: Double declaration -!>
    let names : [Int; 5];                 <!- Error: Double declaration -!>
    let flags : [Float; 10];              <!- Error: Double declaration -!>
    @define Const MAX_ITER : Int = 100;   <!- Error: Double declaration -!>

    let names_ : Int; <!- Error: cannot end with an underscore -!>
    let na___mes : Float; <!- Error: cannot contain consecutive underscores -!>
    let very_long_identifier_name: Int;  <!- Identifier too long (>14 characters) - !>     


BeginPg
{
    count := 500000;
    limit := 0;
    totals := 0.0;

    total := 100 / 0; <!-Division by zero-!>
    total := count / 0; <!-Division by zero-!>
    total := total / 0; <!-Division by zero-!>
    total := total / 0.0; <!-Division by zero-!>
    total := total / limit; <!-Division by zero-!>
    total := total / totals; <!-Division by zero-!>

    names[500] := 10; <!- Error: (index out of bounds) -!>
    names[1] := names[0] + (names[500]+5); <!- Error: (index out of bounds) -!>
    names[6] := 1;     <!- Error: (index out of bounds) -!>

    names[5.5] := 1; <!- Array index must be Int, got 'Float' -!>
    names[total] := 1; <!- Array index must be Int, got 'Float' -!>


    count := total;      <!- Error: Assign Float to Int -!>
    count := 0.0;        <!- Error: Assign Float to Int -!>


    flags := 123; <!- Error: Assign to Array -!>
    names := 50;  <!- Error: Assign to Array -!> 
    int_array := int_array - int_array; <!- Error: Assign to Array -!>
    int_array := int_array - 5; <!- Error: Assign to Array -!>
    int_array := 5 - int_array; <!- Error: Assign to Array -!>
    int_array := int_array AND 0; <!- Error: Assign to Array -!>
    int_array := int_array * 5; <!- Error: Assign to Array -!>
    int_array := int; <!- Error: Assign to Array -!>
    float_array := int_array; <!- Error: Assign to Array -!>
    total := int_array; <!- Error: Assign Array to variable -!>

    MAX_ITER := 10;     <!- Error: Assign to constant -!>

    undeclared_var := 5; <!- Error: Undeclared identifier -!>
    total := undeclared_var; <!- Error: Undeclared identifier -!>

    if (5.5) then {                              <!- Non-Int condition in if - !>         
        x := 10;     
    }  

    do {         
        x := x - 1;     
    } while (total);                               <!- Non-Int condition in while - !> 


    for MAX_ITER from 1 to 10 step 1 {               <!- Constant used as loop variable - !>         
        i := 5;     
    }  

    for float_array from 1 to 10 step 1 {              <!- Array used as loop variable - !>         
        i := 5;     
    }  

    for i from 1.5 to 10 step 1 {              <!- Non-integer 'from' expression - !>         
        i := i;     
    }  

    for i from 1 to 10.5 step 1 {              <!- Non-integer 'to' expression - !>         
        i := i;     
    }  

    for i from 1 to 10 step 1.5 {              <!- Non-integer 'step' expression - !>         
        x := i;     
    }  

}
EndPg;