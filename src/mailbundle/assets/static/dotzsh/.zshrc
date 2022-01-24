### this configuration takes your standard user conf + confdir/activate


# sometimes your configuration doesn't like screen term. We like it, instead
if [[ $TERM =~ screen ]]; then
	_mailbundle_term=$TERM
fi
confd=$(readlink -f ${ZDOTDIR}/..)
if [ -r ~/.zshrc ]; then
	#. ~/.zshrc
fi
if [[ -n $_mailbundle_term ]]; then
	#TERM=$_mailbundle_term
fi
source $confd/activate
