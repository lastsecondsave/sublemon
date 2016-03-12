// SYNTAX TEST "Packages/Sublemon/java_spec/java.sublime-syntax"

package some.package.here.with_123;
//<- meta.package.java
//      ^ meta.package.java storage.type.package.java

import static
//<- meta.import.java
//     ^ meta.import.java keyword.import.static.java

import static some.package.here.*;
//<- meta.import.java
//            ^ meta.import.java storage.type.package.java
//                              ^ meta.import.java storage.type.asterisk.java

import static some.package.here.ClassName;
//                              ^ meta.import.java storage.type.java

import static some.package.here.ClassName.CONSTANT;
//                                        ^ constant.user.java

import static some.package.here.ClassName.C;
//                                        ^ constant.user.java

import some.package.here.CLASS;
//                       ^ meta.import.java storage.type.java

import some.package.here.C;
//                       ^ meta.import.java storage.type.java

@interface Annotation {
// <- meta.class.identifier.java storage.type.modifier.java
}

public @interface Annotation {
//     ^ meta.class.identifier.java storage.type.modifier.java
}

interface Interface<T> {
// <- meta.class.identifier.java storage.type.modifier.java
//                  ^ meta.class.identifier.java meta.generic.java storage.type.generic.java
}

for (String str : strings) {
//          ^^^ variable.parameter.java
//              ^ keyword.operator.java
}

class ClassName extends some.package.Parent.Class<T> implements some.package.ParentClass<T>, some.package.Parent.Class<T>{
//                                   ^ meta.extends.statement.java storage.type.java
//                                   ^        meta.extends.statement.java storage.type.java
//                                                                           ^ meta.implements.statement.java storage.type.java
//                                                                                                        ^ meta.implements.statement.java storage.type.java
    some.package.T nonGeneric;
//               ^ storage.type.java
    T generic;
//  ^ storage.type.generic.java

    List<T> listWithGeneric;
//       ^ storage.type.generic.java

    Map.Entry<String, int[]> complexType;
//                    ^ storage.type.primitive.java

    public static void main(String[] args) throws some.package.Exception, some.package.Exception.Inner {
//                                                             ^ meta.throws.statement.java storage.type.java
//                                                                                     ^ meta.throws.statement.java storage.type.java
//                                                                                               ^ meta.throws.statement.java storage.type.java

        some.package.Class variable;
//      ^ storage.type.package.java
//                   ^ storage.type.java

        not.package.here().reallyIs;

        not.package.here.as.well;

        some.package.CLASS v;
//      ^ storage.type.package.java
//                   ^ storage.type.java

        CONSTANT;
//      ^^^^^^^^ constant.user.java

        Class.CONSTANT
//            ^^^^^^^^ constant.user.java

        A.isConstant()
//      ^ constant.user.java

        A isClass;
//      ^ storage.type.generic.java
    }
}
