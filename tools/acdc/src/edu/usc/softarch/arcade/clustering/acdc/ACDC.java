package edu.usc.softarch.arcade.clustering.acdc;

import edu.usc.softarch.arcade.clustering.acdc.data.Node;
import edu.usc.softarch.arcade.clustering.acdc.patterns.BodyHeader;
import edu.usc.softarch.arcade.clustering.acdc.patterns.ClusterLast;
import edu.usc.softarch.arcade.clustering.acdc.patterns.DownInducer;
import edu.usc.softarch.arcade.clustering.acdc.patterns.OrphanAdoption;
import edu.usc.softarch.arcade.clustering.acdc.patterns.Pattern;
import edu.usc.softarch.arcade.clustering.acdc.patterns.SubGraph;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;

import javax.swing.tree.DefaultMutableTreeNode;

/**
 * This application facilitates the task of recovering the structure
 * of large and complex software systems in an automatic way by clustering.
 * 
 * The data structure used to represent the components of the software system
 * is a tree, which is clustered incrementally by using several patterns. 
 * 
 * Assumptions made:
 * ACDC will cluster the children of the root in the input.
 * Once an object has been clustered, it is never removed from its cluster
 * (but it might get further clustered within its cluster)
 */
public class ACDC {
	//region PUBLIC INTERFACE
	public static void main(String[] args) throws IOException {
		String inputName = args[0];
		String outputName = args[1];

		// EPL484 change: optional parameters so that the experiments suggested
		// in the course tutorial (max cluster size, set of patterns) can be run.
		int maxClusterSize = args.length > 2 ? Integer.parseInt(args[2]) : 20;
		String patterns = args.length > 3 ? args[3] : "bso";
		run(inputName, outputName, maxClusterSize, patterns);
	}

	public static void run(String inputName, String outputName)
			throws IOException {
		run(inputName, outputName, 20, "bso");
	}

	/**
	 * @param maxClusterSize used by the SubGraph pattern
	 * @param patterns any combination of b (BodyHeader), s (SubGraph),
	 *                 o (OrphanAdoption)
	 */
	public static void run(String inputName, String outputName,
			int maxClusterSize, String patterns) throws IOException {

		// Create a tree with a dummy root
		Node dummy = new Node("ROOT", "Dummy");
		DefaultMutableTreeNode root = new DefaultMutableTreeNode(dummy);
		dummy.setTreeNode(root);
		Pattern inducer = new DownInducer(root);

		// Populate the tree from the input file
		TAInput.readInput(inputName, root);

		Collection<Pattern> vpatterns = new ArrayList<>();
		if (patterns.contains("b")) vpatterns.add(new BodyHeader(root));
		if (patterns.contains("s")) vpatterns.add(new SubGraph(root,maxClusterSize));
		if (patterns.contains("o")) vpatterns.add(new OrphanAdoption(root));

		// Induce all edges
		Collection<Node> allNodes = Pattern.allNodes(root);
		Pattern.induceEdges(allNodes);

		// Execute the patterns
		for (Pattern p : vpatterns)
			p.execute();

		// Take care of any objects that were not clustered
		Pattern c = new ClusterLast(root);
		c.execute();

		// Create output file
		inducer.execute();
		RSFOutput.writeOutput(outputName, root);
	}
	//endregion
}
