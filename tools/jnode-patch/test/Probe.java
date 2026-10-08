// Prints the class dependency graph that JNode builds (ClassycleWorker) for a jar.
import jnode.modelEntities.ClassAnalysis; import jnode.workers.ClassycleWorker; import java.util.*;
public class Probe { public static void main(String[] a){
  List<ClassAnalysis> l = new ClassycleWorker(a[0], true).getClassAnalysis();
  l.sort(Comparator.comparing(ClassAnalysis::getName));
  for (ClassAnalysis c : l) System.out.println(c.getName()+" -> "+new TreeSet<>(c.getClassesesForDependency()));
}}
