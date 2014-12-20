def rowcol_from_template():
	template_tab = S.shape[2] - 1
	for row, tab in S.row_heights.keys():
		if tab == template_tab:
			for t in xrange(template_tab):
				S.row_heights[(row, t)] = \
					S.row_heights[(row, tab)]

	for col, tab in S.col_widths.keys():
		if tab == template_tab:
			for t in xrange(template_tab):
				S.col_widths[(col, t)] = \
					S.col_widths[(col, tab)]

def cell_attributes_from_template():
	template_tab = S.shape[2] - 1
	new_cell_attributes = []
	for attr in S.cell_attributes:
		if attr[1] == template_tab:
			for t in xrange(template_tab):
				new_attr = (attr[0], t, attr[2])
				new_cell_attributes.append(new_attr)
	S.cell_attributes.extend(new_cell_attributes)

cell_attributes_from_template()
rowcol_from_template()
