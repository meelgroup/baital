grammar bool;

LPAREN : '(';
RPAREN : ')';
NEGATION : 'not';
TOPOP : ('||' | '&&') ;
MIDDLEOP : ('=>'); 
COMP : ('=' | '<' | '>' | '<=' | '>=');
ID : ('a'..'z'|'A'..'Z'|'0'..'9'|'_'|'.') ('a'..'z'|'A'..'Z'|'0'..'9'|'_'|'.')*;
WS : [ \t\r\n]+ -> skip;

ident : var=ID {} | LPAREN ex=expr RPAREN {};
term : id=ident {} | id=ident COMP id2=ident {} ;
expr_inner3: t=term {} | NEGATION t=term  {};
expr_inner2 : e=expr_inner3 {} | e1=expr_inner3 MIDDLEOP e2=expr_inner2 {};
expr_inner : e=expr_inner2 {} | e1=expr_inner2 top=TOPOP e2=expr_inner {};
expr : ei=expr_inner | LPAREN e=expr RPAREN;

formula : expr;
