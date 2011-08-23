package gui;

import ij.IJ;
import ij.ImageJ;
import ij.ImagePlus;
import ij.WindowManager;
import ij.gui.ImageWindow;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;

import xmipp.Program;
import javax.swing.BorderFactory;
import javax.swing.ButtonGroup;
import javax.swing.DefaultComboBoxModel;
import javax.swing.Icon;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JRadioButton;
import javax.swing.JScrollPane;
import javax.swing.JSlider;
import javax.swing.JTable;
import javax.swing.JTextField;
import javax.swing.ListSelectionModel;
import javax.swing.UIManager;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import browser.windows.ImagesWindowFactory;

import model.Constants;
import model.Family;
import model.Micrograph;
import model.ExecutionEnvironment;
import model.ParticlePicker;
import model.Particle;
import model.XmippJ;

enum Tool {
	IMAGEJ, PICKER
}

enum Shape {
	CIRCLE, RECTANGLE, BOTH
}

public class ParticlePickerJFrame extends JFrame implements ActionListener {

	private JSlider sizesl;
	private JRadioButton circlerbt;
	private JRadioButton rectanglerbt;
	private ButtonGroup shapebg;
	private ParticlePickerCanvas canvas;
	private JTextField sizetf;
	private Tool tool = Tool.PICKER;
	private JRadioButton bothrbt;
	private Shape shape;
	private JMenuBar mb;
	private JComboBox familiescb;
	private JButton geditbt;
	private ParticlePicker ppicker;
	private JLabel colorlb;
	private ColorIcon coloricon;
	private Color color;
	private JPanel familypn;
	private JPanel symbolpn;
	private String activemacro;
	private JPanel micrographpn;
	private JTable micrographstb;
	private ImageWindow iw;
	private boolean changed;
	private JMenuItem savemi;
	private MicrographsTableModel micrographsmd;
	Micrograph micrograph;
	private JPanel buttonspn;
	private JButton trainbt;
	private JButton autopickbt;
	private JLabel iconlb;
	private JPanel steppn;
	private JButton resetbt;
	private JButton nextbt;

	public Shape getShape() {
		return shape;
	}

	public Tool getTool() {
		return tool;
	}

	

	public ParticlePicker getParticlePicker() {
		return ppicker;
	}

	public Family getFamily() {
		return (Family) familiescb.getSelectedItem();
	}

	public ParticlePickerJFrame() {

		ppicker = ParticlePicker.getInstance();

		initComponents();
		initializeCanvas();
	}
	
	public Micrograph getMicrograph()
	{
		return micrograph;
	}



	private void initComponents() {
		try {
			UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		addWindowListener(new WindowAdapter() {
			public void windowClosing(WindowEvent winEvt) {
				if(changed)
				{
					int result = JOptionPane.showConfirmDialog(ParticlePickerJFrame.this, "Save changes before closing?", "Message", JOptionPane.YES_NO_OPTION);
					if(result == JOptionPane.OK_OPTION)
						ParticlePickerJFrame.this.saveChanges();
				}
				System.exit(0);
			}

		});
		setResizable(false);
		setDefaultCloseOperation(DISPOSE_ON_CLOSE);
		setTitle("Particle Picker");
		initPPMenuBar();
		setJMenuBar(mb);

		GridBagConstraints constraints = new GridBagConstraints();
		constraints.insets = new Insets(0, 5, 0, 5);
		constraints.anchor = GridBagConstraints.WEST;
		setLayout(new GridBagLayout());

		initStepPane();
		add(steppn, WindowUtils.updateConstraints(constraints, 0, 0, 3));
		

		initFamilyPane();
		add(new JLabel("Family:"),
				WindowUtils.updateConstraints(constraints, 0, 1, 1));
		add(familypn,
				WindowUtils.updateConstraints(constraints, 1, 1, 1));
		
		initSymbolPane();
		add(symbolpn,
				WindowUtils.updateConstraints(constraints, 0, 2, 3));

		

		initMicrographsPane();
		add(micrographpn, WindowUtils.updateConstraints(constraints, 0, 3, 3));

			initButtonsPane();
			add(buttonspn, WindowUtils.updateConstraints(constraints, 0, 4, 3));
		pack();
		WindowUtils.centerScreen(0.9, this);
		setVisible(true);
	}
	
	

	private void initStepPane()
	{
		steppn = new JPanel();
		JLabel manuallb = new JLabel("Manual");
		manuallb.setFont(new Font(manuallb.getFont().getName(), Font.BOLD, manuallb.getFont().getSize()));
		JLabel supervisedlb = new JLabel("Supervised");
		steppn.add(manuallb);
		steppn.add(new JLabel(" >> "));
		steppn.add(supervisedlb);
		
	}


	private void initFamilyPane() {
		familypn = new JPanel();
		
		// Setting edit button
		geditbt = new JButton("Edit");
		familypn.add(geditbt);

		// Setting combo
		familiescb = new JComboBox(ppicker.getFamilies().toArray());
		familypn.add(familiescb);

		// Setting color
		color = getFamily().getColor();
		familypn.add(new JLabel("Color:"));
		coloricon = new ColorIcon(color);
		colorlb = new JLabel(coloricon);
		familypn.add(colorlb);

		// Setting slider
		int size = getFamily().getSize();
		familypn.add(new JLabel("Size:"));
		sizesl = new JSlider(0, 500, size);
		int height = (int)sizesl.getPreferredSize().getHeight();
		sizesl.setPreferredSize(new Dimension(150, height));
		
		familypn.add(sizesl);
		sizetf = new JTextField(3);
		sizetf.setText(Integer.toString(size));
		familypn.add(sizetf);

		// Setting pane listeners

		geditbt.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				new EditFamiliesJDialog(ParticlePickerJFrame.this, true);
				
			}
		});

		sizetf.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				int size = Integer.parseInt(sizetf.getText());
				switchSize(size);

			}
		});

		sizesl.addChangeListener(new ChangeListener() {

			@Override
			public void stateChanged(ChangeEvent e) {
				int size = sizesl.getValue();
				switchSize(size);
			}
		});

		familiescb.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				color = (getFamily().getColor());
				colorlb.setIcon(new ColorIcon(color));
				sizesl.setValue(getFamily().getSize());
				ParticlePickerJFrame.this.micrographsmd.fireTableDataChanged();
			}
		});
	}
	
	private void initSymbolPane() {

		symbolpn = new JPanel();
		symbolpn.setBorder(BorderFactory.createTitledBorder("Symbol"));
		shapebg = new ButtonGroup();
		circlerbt = new JRadioButton("Circle");
		shapebg.add(circlerbt);
		rectanglerbt = new JRadioButton("Rectangle");
		shapebg.add(rectanglerbt);
		bothrbt = new JRadioButton("Both");
		bothrbt.getModel().setSelected(true);
		shape = shape.BOTH;
		shapebg.add(bothrbt);

		symbolpn.add(bothrbt);
		symbolpn.add(circlerbt);
		symbolpn.add(rectanglerbt);

		circlerbt.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				canvas.repaint();
				shape = Shape.CIRCLE;
			}
		});

		rectanglerbt.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				canvas.repaint();
				shape = Shape.RECTANGLE;
			}
		});

		bothrbt.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				canvas.repaint();
				shape = Shape.BOTH;
			}
		});
	}


	public void initPPMenuBar() {
		mb = new JMenuBar();

		// Setting menus
		JMenu filemn = new JMenu("File");
		JMenu filtersmn = new JMenu("Filters");
		JMenu windowmn = new JMenu("Window");
		JMenu helpmn = new JMenu("Help");
		mb.add(filemn);
		mb.add(filtersmn);
		mb.add(windowmn);
		mb.add(helpmn);

		// Setting menu items
		savemi = new JMenuItem("Save");
		savemi.setEnabled(false);
		filemn.add(savemi);
		JMenuItem stackmi = new JMenuItem("Generate Stack...");
		filemn.add(stackmi);

		JMenuItem bcmi = new JMenuItem("Brightness/Contrast...");
		filtersmn.add(bcmi);
		bcmi.addActionListener(this);

		JMenuItem fftbpf = new JMenuItem("Bandpass Filter...");
		filtersmn.add(fftbpf);
		fftbpf.addActionListener(this);
		JMenuItem admi = new JMenuItem("Anisotropic Diffusion...");
		filtersmn.add(admi);
		admi.addActionListener(this);
		JMenuItem msmi = new JMenuItem("Mean Shift");
		filtersmn.add(msmi);
		msmi.addActionListener(this);
		JMenuItem sbmi = new JMenuItem("Substract Background...");
		filtersmn.add(sbmi);
		sbmi.addActionListener(this);
		JMenuItem gbmi = new JMenuItem("Gaussian Blur...");
		filtersmn.add(gbmi);
		gbmi.addActionListener(this);

		JMenuItem particlesmn = new JMenuItem("Particles");
		windowmn.add(particlesmn);
		JMenuItem ijmi = new JMenuItem("ImageJ");
		windowmn.add(ijmi);

		JMenuItem hcontentsmi = new JMenuItem("Help Contents...");
		helpmn.add(hcontentsmi);

		// Setting menu item listeners

		ijmi.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				if(IJ.getInstance() == null)
				{
					new ImageJ(ImageJ.EMBEDDED);
					IJ.getInstance();
				}
				IJ.getInstance().setVisible(true);
			}
		});
		savemi.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				saveChanges();
				JOptionPane.showMessageDialog(ParticlePickerJFrame.this, "Data saved successfully");
				((JMenuItem)e.getSource()).setEnabled(false);
			}
		});
		stackmi.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
			

			}
		});

		
		

		particlesmn.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				List<ImagePlus> imgs = new ArrayList<ImagePlus>();
				Family f = ParticlePickerJFrame.this.getFamily();
				for(Particle p: getMicrograph().getFamilyData(f).getParticles())
					imgs.add(p.getImage());
				String filename = XmippJ.saveTempImageStack(imgs);
				ImagesWindowFactory.openFileAsImage(filename);
//				new MicrographParticlesJDialog(XmippParticlePickerJFrame.this, XmippParticlePickerJFrame.this.micrograph);
			}
		});

	}
	
	
	
	
	@Override
	public void actionPerformed(ActionEvent e) {
		try
		{
			activemacro = ((JMenuItem)e.getSource()).getText();
			IJ.run(activemacro);
		}
		catch(Exception ex)
		{
			ex.printStackTrace();
			JOptionPane.showMessageDialog(this, ex.getMessage());
		}

	}
	
	private void initMicrographsPane()
	{
		GridBagConstraints constraints = new GridBagConstraints();
		constraints.insets = new Insets(0, 5, 0, 5);
		constraints.anchor = GridBagConstraints.WEST;
		micrographpn = new JPanel(new GridBagLayout());
		micrographpn.setBorder(BorderFactory.createTitledBorder("Micrograph"));
		JScrollPane sp = new JScrollPane();
		JPanel ctfpn = new JPanel();
		ctfpn.setBorder(BorderFactory.createTitledBorder("CTF"));
		iconlb = new JLabel();
		ctfpn.add(iconlb);
		micrographsmd = new MicrographsTableModel(this);
		micrographstb = new JTable(micrographsmd);
		micrographstb.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
		micrographstb.getColumnModel().getColumn(0).setPreferredWidth(180);
		micrographstb.getColumnModel().getColumn(1).setPreferredWidth(70);
		micrographstb.setPreferredScrollableViewportSize(new Dimension(250, 200));
		micrographstb.setSelectionMode(ListSelectionModel.SINGLE_INTERVAL_SELECTION);
		micrographstb.getSelectionModel().addListSelectionListener(
				new ListSelectionListener() {
			
			@Override
			public void valueChanged(ListSelectionEvent e) {
				if(e.getValueIsAdjusting())
					return;
				int index = ParticlePickerJFrame.this.micrographstb.getSelectedRow();
				if(index == -1)
					return;//Probably from fireTableDataChanged raised by me.
				micrograph = (Micrograph)ppicker.getMicrographs().get(index);
				initializeCanvas();
				ParticlePickerJFrame.this.iconlb.setIcon(micrograph.getCTFIcon());
			}
		});
		micrographstb.getSelectionModel().setSelectionInterval(0, 0);
		sp.setViewportView(micrographstb);
		micrographpn.add(sp, WindowUtils.updateConstraints(constraints, 0, 0, 1));
		
		micrographpn.add(ctfpn, WindowUtils.updateConstraints(constraints, 1, 0, 1));
	}
	
	private void initButtonsPane()
	{
		buttonspn = new JPanel();
		nextbt = new JButton("Next");
		buttonspn.add(nextbt);
		resetbt = new JButton("Reset");
		buttonspn.add(resetbt);
		nextbt.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				
			}
		});
		resetbt.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				
			}
		});
	}
	

	
	private void switchSize(int size) {
		sizetf.setText(Integer.toString(size));
		sizesl.setValue(size);
		canvas.repaint();
		getFamily().setSize(size);
		setChanged(true);
	}


	

	void initializeCanvas() {
		Micrograph micrograph = getMicrograph();
		if(iw == null )
		{
			canvas = new ParticlePickerCanvas(this);
			iw = new ImageWindow(micrograph.getImage(), canvas);
		}
		else
		{
			canvas.updateMicrograph();
		}
		iw.setTitle(micrograph.getName());
		canvas.setName(micrograph.getName());
	}
	


	public void saveChanges() {

		ppicker.persistFamilies();
		ppicker.persistMicrographs();
		setChanged(false);
	}


	public void updateFamilies() {
		Family item = (Family) familiescb.getSelectedItem();
		DefaultComboBoxModel model = new DefaultComboBoxModel(ppicker
				.getFamilies().toArray());
		familiescb.setModel(model);
		familiescb.setSelectedItem(item);
		color = item.getColor();
		colorlb.setIcon(new ColorIcon(color));
		sizesl.setValue(item.getSize());
		pack();
		canvas.repaint();
		setChanged(true);
	}

	public void addGroup(Family g) {
		if (ppicker.existsFamilyName(g.getName()))
			throw new IllegalArgumentException(
					Constants.getAlreadyExistsGroupNameMsg(g.getName()));
		ppicker.getFamilies().add(g);
		updateFamilies();
	}

	public void removeFamily(Family family) {
		ppicker.getFamilies().remove(family);
		updateFamilies();
	}

	public void setChanged(boolean changed) {
		this.changed = changed;
		savemi.setEnabled(changed);
	}
	
	public void updateMicrographsModel()
	{
		micrographsmd.fireTableDataChanged();
	}

	
	
}
