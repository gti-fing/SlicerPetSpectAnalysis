/*==============================================================================

  Program: 3D Slicer

  Portions (c) Copyright Brigham and Women's Hospital (BWH) All Rights Reserved.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

==============================================================================*/

// Qt includes
#include <QtPlugin>

// EpilepsyCppModule Logic includes
#include <vtkSlicerEpilepsyCppModuleLogic.h>

// EpilepsyCppModule includes
#include "qSlicerEpilepsyCppModuleModule.h"
#include "qSlicerEpilepsyCppModuleModuleWidget.h"

//-----------------------------------------------------------------------------
Q_EXPORT_PLUGIN2(qSlicerEpilepsyCppModuleModule, qSlicerEpilepsyCppModuleModule);

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_ExtensionTemplate
class qSlicerEpilepsyCppModuleModulePrivate
{
public:
  qSlicerEpilepsyCppModuleModulePrivate();
};

//-----------------------------------------------------------------------------
// qSlicerEpilepsyCppModuleModulePrivate methods

//-----------------------------------------------------------------------------
qSlicerEpilepsyCppModuleModulePrivate::qSlicerEpilepsyCppModuleModulePrivate()
{
}

//-----------------------------------------------------------------------------
// qSlicerEpilepsyCppModuleModule methods

//-----------------------------------------------------------------------------
qSlicerEpilepsyCppModuleModule::qSlicerEpilepsyCppModuleModule(QObject* _parent)
  : Superclass(_parent)
  , d_ptr(new qSlicerEpilepsyCppModuleModulePrivate)
{
}

//-----------------------------------------------------------------------------
qSlicerEpilepsyCppModuleModule::~qSlicerEpilepsyCppModuleModule()
{
}

//-----------------------------------------------------------------------------
QString qSlicerEpilepsyCppModuleModule::helpText() const
{
  return "This is a loadable module that can be bundled in an extension";
}

//-----------------------------------------------------------------------------
QString qSlicerEpilepsyCppModuleModule::acknowledgementText() const
{
  return "This work was partially funded by NIH grant NXNNXXNNNNNN-NNXN";
}

//-----------------------------------------------------------------------------
QStringList qSlicerEpilepsyCppModuleModule::contributors() const
{
  QStringList moduleContributors;
  moduleContributors << QString("John Doe (AnyWare Corp.)");
  return moduleContributors;
}

//-----------------------------------------------------------------------------
QIcon qSlicerEpilepsyCppModuleModule::icon() const
{
  return QIcon(":/Icons/EpilepsyCppModule.png");
}

//-----------------------------------------------------------------------------
QStringList qSlicerEpilepsyCppModuleModule::categories() const
{
  return QStringList() << "Epilepsy";
}

//-----------------------------------------------------------------------------
QStringList qSlicerEpilepsyCppModuleModule::dependencies() const
{
  return QStringList();
}

//-----------------------------------------------------------------------------
void qSlicerEpilepsyCppModuleModule::setup()
{
  this->Superclass::setup();
}

//-----------------------------------------------------------------------------
qSlicerAbstractModuleRepresentation* qSlicerEpilepsyCppModuleModule
::createWidgetRepresentation()
{
  return new qSlicerEpilepsyCppModuleModuleWidget;
}

//-----------------------------------------------------------------------------
vtkMRMLAbstractLogic* qSlicerEpilepsyCppModuleModule::createLogic()
{
  return vtkSlicerEpilepsyCppModuleLogic::New();
}
