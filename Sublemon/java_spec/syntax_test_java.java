// SYNTAX TEST "Packages/Sublemon/java_spec/java.sublime-syntax"

import static some.package.here.*;
//                              ^ meta.import.java storage.type.asterisk.java

import static some.package.here.ClassName;
//                              ^ meta.import.java storage.type.java

import static some.package.here.CONSTANT;
//                              ^ constant.user.java

@interface Annotation {
// <- meta.class.identifier.java storage.type.modifier.java
}

public @interface Annotation {
//     ^ meta.class.identifier.java storage.type.modifier.java
}

interface Interface {
// <- meta.class.identifier.java storage.type.modifier.java
}
