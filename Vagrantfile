VAGRANTFILE_API_VERSION = "2"
 
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.
 
  # Every Vagrant virtual environment requires a box to build off of.
  #config.vm.box = "coreos-94"
  #config.vm.box = "precise64"
  config.vm.box = "ubuntu-13.04"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  #config.vm.box_url = "http://storage.core-os.net/coreos/amd64-generic/72.0.0/coreos_production_vagrant.box"
  #config.vm.box_url = "http://storage.core-os.net/coreos/amd64-generic/dev-channel/coreos_production_vagrant.box"
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/raring/current/raring-server-cloudimg-amd64-vagrant-disk1.box"



  #config.vm.synced_folder ".", "/home/core/share", id: "core", :nfs => true, :mount_options => ['nolock,udp,vers=3']

  config.vm.network :private_network, :ip => "10.10.10.15"

  (8000..8098).each do |port|
    config.vm.network :forwarded_port, :host => port, :guest => port
  end

end