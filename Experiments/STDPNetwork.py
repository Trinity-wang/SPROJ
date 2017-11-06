import nest
import pylab
import nest.topology as topp
import nest.raster_plot as raster
import networkx as nx
import matplotlib.pyplot as plt
import numpy

#SET PARAMETERS
numNeurons = 5
poisson_rate = 3000.0
nest.CopyModel("stdp_synapse", "new_stdp", {"Wmax":1.0})
'''
numNeuronsIn = numpy.floor(numNeurons/5)
numNeuronsEx = int(numNeurons-numNeuronsIn)

#Create the neurons for the network
pop = nest.Create("izhikevich", numNeurons)
popEx = pop[:numNeuronsEx]
popIn = pop[numNeuronsEx:]
'''

#DEFINE FUNCTIONS
'''
Take a NEST network as a parameter and generates a networkX graph
'''
def drawNetwork(pop):
	pop_connect_dict = nest.GetConnections(pop)
	G = nx.DiGraph()
	for i in pop:
		G.add_node(i)
	netXEdges = []
	for j in pop_connect_dict:
		x = j[0]
		y = j[1]
		netXEdges.append((x,y))
	G.add_edges_from(netXEdges)
	nx.draw(G, with_labels=True)
	return G

'''
Create a random network (random being defined by the numpy.random.randint function_)
and write it to a csv. Honestly, easier way to do this is numpy.random.randint(0,high=2,10,10)
or something like that, as numpy will create a 2d array with those randints.

However, I did it this way as an exploration into how I could manipulate these arrays for
future purposes, such as implementing other network properties.
'''
def createRandomNetwork(file_name, popSize):
	#generates an adj matrix based on parameters of network, and depending on formula
	#such as small world, clustering, criticality, etc. WIP
	adjMatrix = numpy.zeros((popSize, popSize))
	#ensure that there are no self-connections at each neuron
	for ith_neuron_index in range(len(adjMatrix)):
		adjMatrix[ith_neuron_index][ith_neuron_index] = 0

	#fill out the adj matrix for all other neurons
	for ith_neuron_index in range(len(adjMatrix)):
		for jth_neuron_index in range(len(adjMatrix)):
			if ith_neuron_index != jth_neuron_index:
				adjMatrix[ith_neuron_index][jth_neuron_index]= numpy.random.ranf()
				#adjMatrix[ith_neuron_index][jth_neuron_index]=0.01
	print adjMatrix
	numpy.savetxt("./Syn Weights/"+file_name, adjMatrix, delimiter=",")
	return	

'''
Reads from a csv file for storing weights, connects corresponding
nest neurons, outputs a numpy matrix
'''
def readAndConnect(file, population):
	matrix = numpy.loadtxt(open(file, "rb"), delimiter=",")
	row_pos = 0
	#adjMatrix = []
	for i_neuron_array in matrix:
		col_pos = 0
		for j_connection in i_neuron_array:
			if j_connection == 1.0:
				#adjMatrix.append([row_pos,col_pos])
				nest.Connect([population[row_pos]],[population[col_pos]])
			col_pos = col_pos + 1		
		row_pos = row_pos +1
	'''for i in adjMatrix:
		print "connection:",population[i[0]], " to ", population[i[1]]
		firstConnect = int(i[0])
		secondConnect = int(i[1])
		nest.Connect([population[firstConnect]], [population[secondConnect]])'''
	return matrix

def readAndCreate(file):
	'''Reads from a csv file for storing weights, creates the population indicated,
	returns population'''
	#read a csv file with conections, and rows and columns correspond to individual neurons
	matrix = numpy.loadtxt(open(file, "rb"), delimiter=",")
	#Set parameters of the network by reading the length of the matrix (number of arrays)
	numNeuronsCSV = len(matrix)
	numNeuronsInCSV = numpy.floor(numNeuronsCSV/5)
	numNeuronsExCSV = int(numNeuronsCSV-numNeuronsInCSV)

	#Create the neurons for the network
	pop = nest.Create("izhikevich", numNeuronsCSV)
	#the first 1/5 neurons are inhibitory, the rest are excitatory
	popEx = pop[:numNeuronsExCSV]
	popIn = pop[numNeuronsExCSV:]
	row_pos = 0
	#adjMatrix = []
	#Connect the neurons
	for i_neuron_array in matrix:
		col_pos = 0
		for j_connection in i_neuron_array:
			if j_connection > 0.0:
				#adjMatrix.append([row_pos,col_pos])
				#nest.Connect([pop[row_pos]],[pop[col_pos]])
				
				if row_pos <= numNeuronsInCSV:
					#print "inhib connected"
					nest.Connect([pop[row_pos]],[pop[col_pos]],syn_spec = {"model":"new_stdp","weight":-(j_connection)})
				else:
					nest.Connect([pop[row_pos]],[pop[col_pos]],syn_spec={"model":"new_stdp","weight":j_connection})
			col_pos = col_pos + 1		
		row_pos = row_pos +1
	return pop, popEx, popIn

def outputWeightMatrix(pop):
	nest.GetConnections(pop,pop,"new_stdp")

	return

'''
WIP: Weighted adjacency matrix
'''
'''def connectWithWeights(adjmatrix, pop):
	for i in pop:
		for j in pop:
			syn_weight = adjmatrix [i-1][j-1]
			syn_dict = {"weight": syn_weight}
			nest.Connect([i],[j],syn_spec = syn_dict)
	return'''

'''
WIP: Not really sure if this is necessary anymore, or if it works...
'''
def rasterGenerator(pop):
	spikes = nest.Create("spike_detector",len(pop))
	nest.Connect(pop, spikes)
	plot = nest.raster_plot.from_device(spikes, hist=True)
	return plot


######################################################################################

#     #    #####    #####     ######   #
##   ##   #     #   #    #    #        #
# # # #   #     #   #     #   #        #
#  #  #   #     #   #     #   ######   #
#     #   #     #   #     #   #        #
#     #   #     #   #    #    #        #
#     #    #####    #####     ######   ######

#########################################
'''
TO DO:
-write a separate coding segment that will generate a csv with specific network parameters such as small-worldness, average links, etc
-downsample
'''
######################################################################################

createRandomNetwork("foo.csv",numNeurons)
neuronPop, neuronEx, neuronIn = readAndCreate("./Syn Weights/foo.csv")

#CREATE NODES
noise = nest.Create("poisson_generator",1,{'rate':poisson_rate})
#noiseIn = nest.Create("poisson_generator",1,{'rate':10000.0})
#sine = nest.Create("ac_generator",1,{"amplitude": 100.0, "frequency" :2.0})
spikes = nest.Create("spike_detector", 1)
#spikesEx = spikes[:1]
#spikesIn = spikes[1:]

Ex = 1
d = 1.0
wEx = 1.0
wIn = -1.0

#SPECIFY CONNECTION DICTIONARIES
conn_dict = {"rule": "fixed_indegree", "indegree": Ex,
			"autapses":False,"multapses":False} #connection dictionary
syn_dict_ex = {"delay": d, "weight": wEx}
syn_dict_in = {"delay": d, "weight": wIn}

#SPECIFY CONNECTIONS
nest.Connect(noise, neuronPop,syn_spec = syn_dict_ex)
nest.Connect(neuronPop,spikes)
#nest.Connect(noiseIn, neuronIn, syn_spec = syn_dict_in)
#nest.Connect(neuronEx, spikesEx)
#nest.Connect(neuronIn, spikesIn)

#nest.Connect(multimeter, [1])
#nest.Connect(sine, [1])
#nest.Connect([pop[1]],[pop[2]])
#readAndConnect("./Syn Weights/syn_weights1.csv",pop)

nest.Simulate(1000.0)

#pylab.figure(2)
drawNetwork(neuronPop)
plot = nest.raster_plot.from_device(spikes, hist=True)

'''
The exact neuron spikes and corresponding timings can be obtained by viewing the events
dictionary of GetStatus(spikesEx, "events")
'''

conn = nest.GetConnections(neuronPop,neuronPop,"new_stdp")
connStatus = nest.GetStatus(conn)
connWeight = nest.GetStatus(conn, "weight")

print nest.GetStatus(spikes, "events")
print connStatus
plt.show()
