# Maltego2Arango
This repository began as an effort to create a tool to smoothly turn Maltego graphs into ArangoDB graphs. This has proven to be much more complex in my environment than I initially thought, so for the moment it contains notes on the two file formats and some sample code to get you started doing things from the command line.

Graph Storage:

Both the older MTGX and newer MTGL format are Java archive data (JAR) files. You can unpack them on MacOS using tar -xvf and on Linux the unzip command will accomplish the same.

MTGX has the following subdirectories and the graph structure itself is stored as the same graphml you can obtain by selecting all entities in the Maltego interface and choosing Copy as GraphML as the copy method. The files in Entities with the .entity extension are simply XML.

* ./Cache
* ./Cache/Images
* ./Icons
* ./Icons/Default
* ./Files
* ./Files/Graph1
* ./Graphs
* ./Entities
* 
MTGL has the following subdirectories. The Entities subdirectory still contains XML format .entity files but the graph itself is no longer an atomic human readable file. Instead you will find the graph structure expressed as a number of Apache Lucene indices. This change occurred in 2016 and if you examine the .si files you will find that they mentioned Lucene 5.5.5, the final 5.5 release. As of the creation of this repo, in mid-2025, the current Lucene version is 10.2.

* ./Entities
* ./Icons
* ./Icons/Transportation_Locations
* ./Icons/Technology
* ./Icons/People
* ./Graphs
* ./Graphs/Graph1
* ./Graphs/Graph1/LayoutEntities
* ./Graphs/Graph1/StructureLinks
* ./Graphs/Graph1/DataLinks
* ./Graphs/Graph1/Collection
* ./Graphs/Graph1/StructureEntities
* ./Graphs/Graph1/DataEntities
* ./Graphs/Graph1/LayoutLinks

Lucene is primarily a search library that gets integrated into more complex frameworks, like the ArangoDB graph database, or the Elasticsearch NoSQL system. As such, searching for command line tools will produce dated results and things that seem to be abandonware. Asking ChatGPT or Claude for assistance is an exercise in frustration; both seem to have trained on the same obscure post wherein the author posed a complex question involving Lucene 9.1.3 and received fragmentary responses. Both LLMs will assert that 9.1.3 is most recent, and then chase their tails trying to install a solution.

The historic luke GUI tool was integrated into Lucene 8.1. I think there were some command line utilities, but I've never managed to get this running.

https://github.com/DmitryKey/luke

The thing that installs simply and works with 5.5.5 indices is Lucene Query Tool

https://github.com/joelb-git/lqt

I found making dir explicit was needed in order to use this script from anywhere other than its install directory. The --add-opens java.base/java.nio=ALL-UNNAMED is needed to make this script behave with anything newer than OpenJDK11.

`#! /bin/sh

#dir=$(dirname $0)
dir=/root/lqt
CP=$dir:$dir/target/classes:$(cat $dir/target/classpath.txt)

if [ -e /root/lqt/target/classes/com/basistech/lucene/tools/LuceneQueryTool.class ]; then
    java --add-opens java.base/java.nio=ALL-UNNAMED \
    $JVM_ARGS -Dfile.encoding=UTF-8 -cp $CP com.basistech.lucene.tools.LuceneQueryTool "$@"
else
    echo "Please run 'mvn compile' first."
    exit 1
fi`
